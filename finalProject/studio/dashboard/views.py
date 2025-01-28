from datetime import datetime
from django.core import serializers
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone
import json
from .models import User, Class, Booking

# Create your views here.

def index(request):
	if request.user.is_authenticated:
		# Update class completion status
		now = timezone.now()
		
		# classes on previous dates set to complete
		classes = Class.objects.filter(complete=False, date__lt=now.date())
		for class_instance in classes:
			class_instance.complete = True
			class_instance.save()
		
		# classes earlier today set to complete
		classes = Class.objects.filter(complete=False, time__lt=now.time(), date=now.date())
		for class_instance in classes:
			class_instance.complete = True
			class_instance.save()

		# give number of pages for class history pagination
		if request.user.user_type == "student":
			# get bookings for user
			bookings = Booking.objects.filter(student=request.user)
			
			# get class ids from bookings
			booking_ids = bookings.values_list("booked_class", flat=True)

			# check which of these bookings match a completed class
			history_list = Class.objects.filter(id__in=booking_ids, complete=True).order_by("-date", "-time")
			p = Paginator(history_list, 10)
			num_pages = p.num_pages
		else:
			# get classes for teacher that are completed
			history_list = Class.objects.filter(teacher=request.user, complete=True).order_by("-date", "-time")
			p = Paginator(history_list, 10)
			num_pages = p.num_pages

		return render(request, "dashboard.html", {
			"num_pages": num_pages
		})
	else:
		return HttpResponseRedirect(reverse("navigation:login"))
	

@login_required
def classes(request):
	if request.method == "GET":
		return render(request, "classes.html")
	elif request.method == "POST":
		# take in values as variables and user as creator
		class_date = request.POST.get("date")
		class_time = request.POST.get("time")
		style = request.POST.get("style")
		creator = request.user
		instructor = request.POST.get("instructor")

		# datetime instance processing
		class_datetime = datetime(int(class_date[0:4]), int(class_date[5:7]), int(class_date[8:10]), int(class_time[0:2]), int(class_time[3:5]), 0)
		class_date = class_datetime.date()
		class_time = class_datetime.time()

		# create class object if not already existing class from teacher at same time
		if not Class.objects.filter(teacher=creator, time=class_time, date=class_date).exists():
			created_class = Class.objects.create(teacher=creator, instructor_name=instructor, style=style, time=class_time, date=class_date, complete=False)
			created_class.save()
		else:
			messages.error(request, "Existing class for teacher at this time.")
		return HttpResponseRedirect(reverse("classes"))
		
#get classes API needed to receive JS fetch requests for class schedule on requested day
@login_required
def get_classes(request, search_date):
	# Update class completion status
	now = timezone.now()
	
	# classes on previous dates set to complete
	classes = Class.objects.filter(complete=False, date__lt=now.date())
	for class_instance in classes:
		class_instance.complete = True
		class_instance.save()
	
	# classes earlier today set to complete
	classes = Class.objects.filter(complete=False, time__lt=now.time(), date=now.date())
	for class_instance in classes:
		class_instance.complete = True
		class_instance.save()

	search_year = int(search_date[0:4])
	search_month = int(search_date[5:7])
	search_day = int(search_date[8:10])

	# create datetime instance to filter classes
	search_date = datetime(search_year, search_month, search_day).date()
	results = Class.objects.filter(date=search_date).order_by("time")

	# check for each class if user has already booked
	for result in results:
		try:
			Booking.objects.get(student=request.user, booked_class=result)
			result.booked = True
			result.save()
		except Booking.DoesNotExist:
			result.booked = False
			result.save()

	# for each class check how many bookings
	for result in results:
		try:
			count = Booking.objects.filter(booked_class=result).count()
			result.count = count
			result.save()
		except Booking.DoesNotExist:
			result.count = 0
			result.save()

	# Create a list of dictionaries from the queryset
	results_list = []
	for result in results:
		result_dict = {
			'time': result.time.strftime('%H:%M:%S'),
			'style': result.style,
			'instructor_name': result.instructor_name,
			'complete': result.complete,
			'booked': result.booked,
			'count': result.count
		}
		results_list.append(result_dict)

	# Serialize the list of dictionaries to JSON
	class_list = json.dumps(results_list)
	return HttpResponse(class_list, content_type="application/json")


@login_required
def book_class(request, search_time, search_date, instructor_name):
	search_year = int(search_date[0:4])
	search_month = int(search_date[5:7])
	search_day = int(search_date[8:10])
	search_hour = int(search_time[0:2])
	search_minute = int(search_time[3:5])

	# create datetime instance to filter classes
	search = datetime(search_year, search_month, search_day, search_hour, search_minute)
	search_date = search.date()
	search_time = search.time()

	# find class instance to book
	try:   
		search_class = Class.objects.get(date=search_date, time=search_time, instructor_name=instructor_name)
	except Class.MultipleObjectsReturned:
		return HttpResponse(status=500)

	# count existing bookings for this class
	count = Booking.objects.filter(booked_class=search_class).count()

	# first search for existing booking to prevent duplicate and ensure class capacity not already reached
	if not Booking.objects.filter(student=request.user, booked_class=search_class).exists() and count < 12:
		# create booking
		booking = Booking.objects.create(student=request.user, booked_class=search_class)
		booking.save()
	else:
		return HttpResponse(status=400)
	return HttpResponse(status=201)


@login_required
def cancel_class(request, search_time, search_date, instructor_name):
	search_year = int(search_date[0:4])
	search_month = int(search_date[5:7])
	search_day = int(search_date[8:10])
	search_hour = int(search_time[0:2])
	search_minute = int(search_time[3:5])

	# create datetime instance to filter classes
	search = datetime(search_year, search_month, search_day, search_hour, search_minute)
	search_date = search.date()
	search_time = search.time()

	if request.user.user_type == "student":
		# find class instance to cancel
		try:   
			search_class = Class.objects.get(date=search_date, time=search_time, instructor_name=instructor_name)
		except Class.MultipleObjectsReturned:
			return HttpResponse(status=500)

		# confirm existing booking before deletion
		try:
			booking = Booking.objects.get(student=request.user, booked_class=search_class)
			# delete booking
			booking.delete()
		except Class.DoesNotExist:
			return HttpResponse(status=400)
	else:
		# find class instance to cancel
		try:   
			search_class = Class.objects.get(date=search_date, time=search_time, teacher=request.user)
		except Class.MultipleObjectsReturned:
			return HttpResponse(status=500)
		
		# find all bookings associated with this class
		bookings = Booking.objects.filter(booked_class=search_class)

		# delete all bookings
		for booking in bookings:
			booking.delete()

		# delete class
		search_class.delete()
	return HttpResponse(status=204)


@login_required
def class_history(request, page):
	if request.user.user_type == "student":
		# get bookings for user
		bookings = Booking.objects.filter(student=request.user)
		
		# get class ids from bookings
		booking_ids = bookings.values_list("booked_class", flat=True)

		# check which of these bookings match a completed class
		history_list = Class.objects.filter(id__in=booking_ids, complete=True).order_by("-date", "-time")
		p = Paginator(history_list, 10)
		history_list = p.page(page)

		# serialise and return this list
		history = serializers.serialize("json", history_list)
		return HttpResponse(history, content_type="application/json")
	elif request.user.user_type == "teacher":
		# get completed classes for teacher
		history_list = Class.objects.filter(teacher=request.user, complete=True).order_by("-date", "-time")
		p = Paginator(history_list, 10)
		history_list = p.page(page)

		# serialise and return as JSON
		history = serializers.serialize("json", history_list)
		return HttpResponse(history, content_type="application/json")


@login_required
def upcoming_classes(request):
	if request.user.user_type == "student":
		# get bookings for user
		bookings = Booking.objects.filter(student=request.user)
		
		# get class ids from bookings
		booking_ids = bookings.values_list("booked_class", flat=True)

		# check which of these bookings are not yet completed
		upcoming_list = Class.objects.filter(id__in=booking_ids, complete=False).order_by("-date", "-time")

		# serialise and return this list
		upcoming = serializers.serialize("json", upcoming_list)
		return HttpResponse(upcoming, content_type="application/json")
	elif request.user.user_type == "teacher":
		# get non-completed classes for teacher
		upcoming_list = Class.objects.filter(teacher=request.user, complete=False).order_by("-date", "-time")

		# serialise and return as JSON
		upcoming = serializers.serialize("json", upcoming_list)
		return HttpResponse(upcoming, content_type="application/json")


@login_required
def stats(request):
	if request.user.user_type == "student":
		# get bookings for user
		bookings = Booking.objects.filter(student=request.user)
		
		# get class ids from bookings
		booking_ids = bookings.values_list("booked_class", flat=True)

		# check which of these bookings match a completed class
		history_list = Class.objects.filter(id__in=booking_ids, complete=True).order_by("-date", "-time")

		# count number of classes
		count = history_list.count()

		# most attended style
		favourite_search = history_list.annotate(frequency=Count("style")).order_by("-frequency")[:1]
		favourite = favourite_search[0].style

		# favourite instructor
		teacher_search = history_list.annotate(fav_teacher=Count("instructor_name")).order_by("-fav_teacher")[:1]
		fav_teacher = teacher_search[0].instructor_name

		# Create a dictionary from the queryset
		stats = {
			'count': count,
			"fav_style": favourite,
			"fav_teacher": fav_teacher
		}

	else:
		# get completed classes for teacher
		classes = Class.objects.filter(teacher=request.user, complete=True)

		# count number of classes
		count = classes.count()

		# most taught style
		favourite_search = classes.annotate(frequency=Count("style")).order_by("-frequency")[:1]
		favourite = favourite_search[0].style

		# Create a dictionary from the queryset
		stats = {
			'count': count,
			"fav_style": favourite
		}

	# Serialize the dictionary to JSON
	stats_JSON = json.dumps(stats)
	return HttpResponse(stats_JSON, content_type="application/json")
