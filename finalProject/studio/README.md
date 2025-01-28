# Project Name:
Studio

# Brief Overall Description:
Studio is a web application created for a fictional yoga studio called BreathSpace that schedules and takes bookings for classes.
Students and teachers have distinct experiences within the application. Students may log on, search for upcoming classes and create or cancel bookings. Teachers may log on and create or cancel classes.
Additionally, each user has access to their own dashboard which holds a history of their previously attended / taught classes and any upcoming classes, plus a small stats section depending on their user type.

# How to Run Application:
To run BreathSpace, navigate to the finalProject/studio directory and run python3 manage.py runserver.

Once you open the application, you will be presented with the landing page for the website. Click the "Log In" option from the navbar to reach the login page. There is a link at the bottom of the login card which will take you to the register / sign up page alternatively. Create a student / teacher account.

I recommend creating a teacher account first and going to the "Classes" page using the navbar. Create a class using the provided form so that there is at least one listing to search for and that will show up in your dashboard. You can then create a student account and search for and book this class. The booked class will then show up in your student dashboard.

# Files in Project:
## Applications:
There are two applications included in this project:

### Navigation:
The navigation application is used for the initial front-end of the website as well as the log in and sign up processes. 

The views.py file contains views that present the user with the initial landing page for the site and an about page giving history on the business. There are then 3 views for login, registration of a new account and logout.

Since all pages in the project use the same layout html template, I configured the Django settings to store all project templates within the navigation directory to make template extension simpler and keep all similar files together.
Similarly, for simplicity I have set up the project so that all the static files are stored in this application's directory. You will thus find all the javascript files for the project and the images used for the landing and about us pages in this folder.

### Dashboard:
The main functions of the project takes place in this application. The dashboard application handles class creation and booking and the creation of the user's student / teacher dashboard. 

The project models are stored here in the models.py file:
- User: Based on Django's abstractUser with the addition of a user_type field that tracks if the user is a student or teacher. Commonly called throughout the project.
- Class: Each instance is a created class in the system that can be booked. Holds a foreign key to locate the teacher that createdit, an instructor_name field to display with the class advertisement to students, the yoga style of the class, date and time fields for when the class takes place and a complete field that marks if the class has taken place or not.
- Booking: Each instance is a booking of a class by a particular student. Just holds foreign keys to link the two objects.

Looking at the dashboard views.py file:
- Index: Takes the user to their dashboard if logged in, if not takes them to the login view of the navigation application. I added code to this view to update the classes database to ensure the system knows which classes have already taken place before displaying info on upcoming classes and user's class history. I also added the number of pages required for pagination of the class history table as a context variable to the dashboard template through this view. This seemed the easiest solution when implementing pagination.
- Classes: This brings up the classes.html page for the user. If the user is a teacher then they will have an additional card displayed with a form that enable class creation. This is the purpose of the POST method handling here which allows class creation. One notable feature is that the teacher will be prevented from creating two classes at the same time.
- Get Classes: This view is an API used with the search class schedule card on the classes.html page. The classes.js file contains a fetch request to this API when the search button is pressed that gets the classes for the chosen date. First the completion status of classes in the database is updated. Classes for that date are then found and checked to see if the user already has a booking for that class created. The user will be presented with a book button for the class if not already booked and a cancel button for that class if they already have a booking. Class capacity is also calculated by checking how many bookings exist for that class. If the class capacity is already reached the user will not be able book the class. Data is finally jsonified and returned.
- Book Class: API that handles class bookings by student users. Sent by the classes.js file when the student presses the "Book" button. Includes a server-side check that the user doesn't already have a booking. Note that class capacity on the class schedule is updated by the classes.js file when a booking is created.
- Cancel Class: If the user is a student this API deletes their booking for this class. There is a check to ensure a booking exists for the user for this class before deletion. If the user is a teacher this API will delete their advertised class after deleting all student bookings associated with this class. The teacher will get confirmation on the page that the class has been cancelled. Note that this API can be initiated by a fetch request from the class schedule on the classes.html page using the classes.js file or from the dashboard's upcoming class table using the dashboard.js file.
- Class History: API requested by the dashboard.js file which gets the user's previously completed classes. If the user is a student then the API finds any bookings associated with their account and filters the classes model to find which of these booked classes have taken place. If the user is a teacher the search is simpler with classes associated with that teacher filtered to find which have taken place. Pagination is applied here as the class history table can be expected to grow over time. 10 results are restricted to each page. The classes.js file will continue to fetch to this API when the previous / next page is requested by the user.
- Upcoming Classes: API requested by the dashboard.js file which gets the user's upcoming classes. Very similar to the class history API but classes are filtered as not completed. Pagination is not implemented here as classes will move to class history once they are completed so this list is not expected to grow much.
- Stats: API accessed by the dashboard.js file that, depending on user type, calculates basic stats for the user and returns the jsonified results to populate the user's stats page on the dashboard.

# Distinctiveness and Complexity
This project is distinct from other CS50W projects in that it is a scheduling and booking system for fitness classes. This could be similarly extended to any appointment-based service. Previous projects encountered as part of the course were based on social networking, email, e-commerce or transport. In these previous course projects the basic use of dynamic page generation, fetch requests, Django templates and APIs were introduced but were not implemented in the manner this project presents. This project uses these features to build a system capable of creating, searching and booking appointments and thus puts a lot more emphasis in handling and using time and date data rather than just storing the time a particular object was created. This project is also distinct in its use of user types throughout, meaning that each Django view, API, JavaScript function and Django template needs to be configured to handle requests differently depending on the user type.

This project satisfies the requirement for complexity through its use of multiple user types, two application, 3 object models and the integration of a public homepage advertising the business rather prior to login / account creation rather than just serving existing customers with applications. The project complexity was also increased due to the requirement to handle date and time instances both in the front-end where users are either scheduling or booking classes and in the back end where dates and times need to be converted into various formats to interact with the Django object models. The project implements multiple APIs to handle data fetch requests from the user in order to implement dynamic search and class schedule generation features. APIs themselves are complex as their behaviour is dependent on the type of user logged in and requesting the information as a request from a student user will be handled differently than a request from a teacher user. The project is mobile responsive with page layouts adapting to smaller screens and pages are interactive, responding to user inputs and constantly ensuring the most up-to-date information is available to the user. 