import json
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse

from .models import User, Post, Follow, Like


def index(request):
    if request.method == "POST":
        # extract data from request
        user = request.user
        text = request.POST["text"]

        # Create new post
        post = Post.objects.create(user=user, text=text)
        return HttpResponseRedirect(reverse("index"))
    elif request.method == "GET":
        # find number of pages of posts for paginator
        get_posts = Post.objects.all().order_by("-id")
        p = Paginator(get_posts, 10)
        num_pages = p.num_pages
        return render(request, "network/index.html", {
            "num_pages": num_pages
        })
    else:
        return HttpResponse(status=404)


@login_required
def get_posts(request, page):
    if request.method == "GET":
        # Get all the posts created so far, most recent first
        get_posts = Post.objects.all().order_by("-id")
        p = Paginator(get_posts, 10)

        # page of posts
        posts = p.page(page)

        # serialize each post and check if user has liked it already
        serialized_posts = []
        for post in posts:
            serialized_post = post.serialize()
            # try get existing like for post
            try:
                likes = Like.objects.get(user=request.user, post=post)
                serialized_post["liked"] = True
            except Like.DoesNotExist:
                serialized_post["liked"] = False
            serialized_post["owner"] = post.user.username
            serialized_posts.append(serialized_post)
        return JsonResponse(serialized_posts, safe=False)


@login_required
def profile(request, username):
    # get profile corresponding to username
    profile = User.objects.get(username=username)

    # get profile posts to find number of pages
    get_posts = Post.objects.filter(user=profile).order_by("-id")
    p = Paginator(get_posts, 10)
    num_pages = p.num_pages

    # get number of users profile is following
    following_count = Follow.objects.filter(follower=profile).count()

    # see if user is following already
    try:
        Follow.objects.get(follower=request.user, followed=profile)
        following = True
    except Follow.DoesNotExist:
        following = False

    return render(request, "network/profile.html", {
        "num_pages": num_pages,
        "profile": profile,
        "following": following,
        "following_count": following_count
    })


@login_required
def get_profile_posts(request, username, page):
    if request.method == "GET":
        # get profile corresponding to username
        profile = User.objects.get(username=username)
        
        # Get all the posts created so far, most recent first
        get_posts = Post.objects.filter(user=profile).order_by("-id")
        p = Paginator(get_posts, 10)

        # page
        posts = p.page(page)

        # serialize each post and check if user has liked it already
        serialized_posts = []
        for post in posts:
            serialized_post = post.serialize()
            # try get existing like for post
            try:
                likes = Like.objects.get(user=request.user, post=post)
                serialized_post["liked"] = True
            except Like.DoesNotExist:
                serialized_post["liked"] = False
            serialized_post["owner"] = post.user.username
            serialized_posts.append(serialized_post)
        return JsonResponse(serialized_posts, safe=False)


@login_required
def follow(request):
    if request.method == "POST":
        # get usernames from request
        data = json.loads(request.body)
        user = data["follower"]
        profile = data["followed"]

        # identify user objects
        follower = User.objects.get(username=user)
        followed = User.objects.get(username=profile)

        # if not already existing, create follow instance
        follow, created = Follow.objects.get_or_create(follower=follower, followed=followed)

        if created:
            # add 1 to profile follower count
            followed.followers += 1
            followed.save()
        return JsonResponse({"followers": followed.followers}, status=201)
    else:
        return HttpResponse(status=404)


@login_required
def unfollow(request):
    if request.method == "POST":
        # get usernames from request
        data = json.loads(request.body)
        user = data["follower"]
        profile = data["followed"]

        # identify user objects
        follower = User.objects.get(username=user)
        followed = User.objects.get(username=profile)

        # if existing, delete follow instance
        try:
            follow = Follow.objects.get(follower=follower, followed=followed)
            follow.delete()

            # remove 1 from profile follower count
            followed.followers -= 1
            followed.save()
        except Follow.DoesNotExist:
            pass
        return JsonResponse({"followers": followed.followers}, status=201)
    else:
        return HttpResponse(status=404)


@login_required
def following(request):
    # get follow objects where the user is following
    follows = Follow.objects.filter(follower=request.user).values_list("followed")

    # get user objects corresponding to these follows
    followed = User.objects.filter(id__in=follows).distinct()

    # get posts from these users
    get_posts = Post.objects.filter(user__in=followed).order_by("-id")
    p = Paginator(get_posts, 10)
    num_pages = p.num_pages

    return render(request, "network/following.html", {
        "num_pages": num_pages,
        "profile": profile,
        "following": following
    })


@login_required
def get_following(request, page):
    if request.method == "GET":
        # get follow objects where the user is following
        follows = Follow.objects.filter(follower=request.user).values_list("followed")

        # get user objects corresponding to these follows
        followed = User.objects.filter(id__in=follows).distinct()

        # get posts from these users
        get_posts = Post.objects.filter(user__in=followed).order_by("-id")
        p = Paginator(get_posts, 10)

        # page 1
        posts = p.page(page)

        # serialize each post and check if user has liked it already
        serialized_posts = []
        for post in posts:
            serialized_post = post.serialize()
            # try get existing like for post
            try:
                likes = Like.objects.get(user=request.user, post=post)
                serialized_post["liked"] = True
            except Like.DoesNotExist:
                serialized_post["liked"] = False
            serialized_post["owner"] = post.user.username
            serialized_posts.append(serialized_post)
        return JsonResponse(serialized_posts, safe=False)
    else:
        return HttpResponse(status=404)


@login_required
def unlike(request):
    if request.method == "DELETE":
        # get data from request
        data = json.loads(request.body)
        user = data["liker"]
        post_id = data["post"]

        # identify objects
        liker = User.objects.get(username=user)
        post = Post.objects.get(id=post_id)

        # if existing, get like instance and delete
        try:
            like = Like.objects.get(user=liker, post=post)
            like.delete()

            # remove 1 from post like count
            post.likes -= 1
            post.save()
        except Follow.DoesNotExist:
            pass
        return JsonResponse({"likes": post.likes}, status=201)
    else:
        return HttpResponse(status=404)
    

@login_required
def like(request):
    if request.method == "POST":
        # get data from request
        data = json.loads(request.body)
        user = data["liker"]
        post_id = data["post"]

        # identify objects
        liker = User.objects.get(username=user)
        post = Post.objects.get(id=post_id)

        # if not already existing, create like instance
        like, created = Like.objects.get_or_create(user=liker, post=post)

        if created:
            # add 1 to profile follower count
            post.likes += 1
            post.save()
        return JsonResponse({"likes": post.likes}, status=201)
    else:
        return HttpResponse(status=404)


@login_required
def edit(request):
    # get data from request
    data = json.loads(request.body)
    new_text = data["new_text"]
    post_id = data["post_id"]


    # get post object
    post = Post.objects.get(id=post_id)

    # check user is editing own post
    if request.user == post.user:
        # update post object
        post.text = new_text
        post.save()
        return HttpResponse(status=200)
    else:
        return HttpResponse(status=403)


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
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


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
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
