from django.contrib.auth.models import AbstractUser
from django.db import models

# user class: holds type of user, student or teacher
class User(AbstractUser):
    pass
    user_type = models.CharField(max_length=7)

# class class: links to teacher, holds style, separate date and time fields. Set complete status when over
class Class(models.Model):
    teacher = models.ForeignKey("User", on_delete=models.CASCADE, related_name="created_class")
    instructor_name = models.CharField(max_length=20)
    style = models.CharField(max_length=10)
    date = models.DateField()
    time = models.TimeField()
    complete = models.BooleanField(default=False)

# booking: instance of booked class, links student to class
class Booking(models.Model):
    student = models.ForeignKey("User", on_delete=models.CASCADE, related_name="booking")
    booked_class = models.ForeignKey("Class", on_delete=models.CASCADE, related_name="booking")
    