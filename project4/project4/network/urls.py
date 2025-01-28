
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("following", views.following, name="following"),

    # API's
    path("posts/<int:page>", views.get_posts, name="get_posts"),
    path("profile/<str:username>/<int:page>", views.get_profile_posts, name="get_profile_posts"),
    path("following/<int:page>", views.get_following, name="get_following"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("like", views.like, name="like"),
    path("unlike", views.unlike, name="unlike"),
    path("edit", views.edit, name="edit")
]
