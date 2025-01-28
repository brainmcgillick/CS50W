from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing, Watchlist, Bid, Comment

Categories = ["Music", "Clothing", "Furniture", "Toys", "Electronics", "Home", "Other"]

class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        exclude = ("owner", "status", "winner")

def index(request):
    listings = Listing.objects.all()
    return render(request, "auctions/index.html", {
        "listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def create(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.owner = request.user
            form.save()
        else:
            print(form.errors)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
        "categories": Categories})
    
def listing(request, listing_id):
    # get listing object from id
    listing = Listing.objects.get(id=listing_id)

    # check if current user is owner of listing
    if request.user == listing.owner:
        owner = True
    else:
        owner = False

    # Set minimum bid, current heighest or starting amount
    try:
        max_value = Bid.objects.filter(listing=listing).aggregate(Max("amount"))["amount__max"]
        min_bid = Bid.objects.get(amount=max_value).amount + Decimal(0.01)
    except ObjectDoesNotExist:
        min_bid = listing.price

    # verify user is signed in
    if request.user.is_authenticated:
        user = request.user
    else:
        user = 0

    # get existing bids for listing
    bids = Bid.objects.filter(listing_id=listing_id)

    # get existing comments for listing
    comments = Comment.objects.filter(listing_id=listing_id)

    # check if user already has listing on watchlist
    if Watchlist.objects.filter(user=user, listing=listing).exists():
        watching = True
    else:
        watching = False

    if request.method == "POST":
        # adding to watchlist
        if request.POST.get("watchlist") == "add" and not watching:
            Watchlist.objects.create(user=user, listing=listing)
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        
        # removing from watchlist
        elif request.POST.get("watchlist") == "remove" and watching:
            Watchlist.objects.filter(user=user, listing=listing).delete()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        
        # creating a bid
        elif request.POST.get("bid") == "bid":
            amount = Decimal(request.POST["amount"])
            amount = round(amount, 2)
            min_bid = round(min_bid, 2)
            if amount >= min_bid:
                Bid.objects.create(user=user, listing=listing, amount=amount)

                # set bidder as current winner of auction
                listing.winner = request.user
                listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        
        # creating a comment
        elif request.POST.get("comment") == "comment":
            text = request.POST["text"]
            Comment.objects.create(user=user, listing=listing, text=text)
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

        # closing auction
        elif request.POST.get("close") == "close":
            listing.status = "closed"
            listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))
        
        # re-open auction
        elif request.POST.get("open") == "open":
            listing.status = "open"
            listing.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id": listing_id}))

        # currently do nothing, to add other functionality
        else:
            return render(request, "auctions/listing.html", {
                "listing": listing,
                "watching": watching
            })
    else:
        listing = Listing.objects.get(id=listing_id)
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "watching": watching,
            "bids": bids,
            "min_bid": min_bid,
            "owner": owner,
            "status": listing.status,
            "winner": listing.winner,
            "comments": comments
        })

@login_required    
def watchlist(request):
    user = request.user
    watchlist = Watchlist.objects.filter(user=user).values_list("listing")
    listings = Listing.objects.filter(id__in=watchlist).distinct()
    return render(request, "auctions/watchlist.html",{
        "listings": listings
    })

def category(request):
    return render(request, "auctions/category.html",{
        "categories": Categories
    })

def category_page(request, page):
    listings = Listing.objects.filter(category=page)
    return render(request, "auctions/category_page.html",{
        "listings": listings,
        "category": page
    })