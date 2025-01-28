from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from dashboard.models import User

# Create your views here.
def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def login_view(request):
    if request.method == "POST":
        # take data from request
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        # if user authenticated, login user
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid email address and/or password."
            })
    elif request.method == "GET":
        return render(request, "login.html")
    
    
def register(request):
    if request.method == "POST":
        # take data from request, username is same as email
        username = request.POST.get("email")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        usertype = request.POST.get("usertype")

        # check password = confirmation
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Password and Password Confirmation Do Not Match."
            })
        
        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, user_type=usertype)
            user.save()
        except IntegrityError:
            return render(request, "register.html", {
                "message": "An Existing Account Matches this Email Address."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))

    elif request.method == "GET":
        return render(request, "register.html")
    

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("navigation:index"))