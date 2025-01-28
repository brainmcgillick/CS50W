from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("classes", views.classes, name="classes"),
    path("get_classes/<str:search_date>", views.get_classes, name="get_classes"),
    path("book_class/<str:search_time>/<str:search_date>/<str:instructor_name>", views.book_class, name="book_class"),
    path("cancel_class/<str:search_time>/<str:search_date>/<str:instructor_name>", views.cancel_class, name="cancel_class"),
    path("class_history/<int:page>", views.class_history, name="class_history"),
    path("upcoming_classes", views.upcoming_classes, name="upcoming_classes"),
    path("stats", views.stats, name="stats")
]
