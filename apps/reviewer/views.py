from django.shortcuts import render, redirect
from models import User, Author, Book, Review # gives us access to django models
from django.contrib import messages # grabs django's `messages` module
from . import helper # grab custom dashboard helper module

# Add extra message levels to default messaging to handle login or registration error generation:
# https://docs.djangoproject.com/en/1.11/ref/contrib/messages/#creating-custom-message-levels
LOGIN_ERR = 50 # Messages level for login errors
REG_ERR = 60 # Messages level for registration errors
REV_ERR = 70 # Messages level for book review errors
LOGOUT_SUCC = 80 # Messages level for logout success messages


def index(request):
    """If GET, load login/registration homepage; if POST, validate and register user."""

    # If POST, validate and register:
    if request.method == "POST":
        # Prepare registration data for validation:
        reg_data = {
            "first_name": request.POST["first_name"],
            "last_name": request.POST["last_name"],
            "email": request.POST["email"],
            "password": request.POST["password"],
            "confirm_pwd": request.POST["confirm_pwd"],
        }
        # Validate registration data:
        validated = User.objects.register_validate(**reg_data) # see `./models.py`, `register_validate()`
        # If errors, reload index page (Django will load error objects):
        try:
            if len(validated["errors"]) > 0:
                print "User could not be registered."
                # Generate Django errors:
                for error in validated["errors"]:
                    # Add error to Django's error messaging:
                    messages.add_message(request, REG_ERR, error, extra_tags="reg_errors")
                # Reload index page:
                return redirect("/")
            else:
                # If this is firing, it means errors returned, but they weren't expected.
                # Could mean someone is spoofing your URL request.
                print "Unexpected errors occurred."
                messages.add_message(request, REG_ERR, "An unexpected error has occurred.", extra_tags="reg_errors")
                return redirect("/")
        except KeyError:
            # If validation successful, create new user and load books page:
            print "User passed validation and has been created..."
            # Set session to validated User:
            print "Setting session data for logged in new user..."
            request.session["user_id"] = validated["logged_in_user"].id
            # Load books page (books dashboard):
            return redirect("/books")

    # If GET, load login/registration page:
    else:
        return render(request, "reviewer/index.html")

def login(request):
    """
    Logs in and validates current user.

    Notes: If successful, retrieve validated user and load books page. Otherwise,
    reload index page with django errors.
    """
    # If POST, validate and login:
    if request.method == "POST":
        # Prepare user submitted data for validation:
        login_data = {
            "email": request.POST["login_email"],
            "password": request.POST["login_password"],
        }
        validated = User.objects.login_validate(**login_data) # pass in login data
        try:
            # If errors, load homepage with errors:
            if len(validated["errors"]) > 0:
                print "User could not be logged in."
                # Generate Django errors:
                for error in validated["errors"]:
                    # Add error to Django's error messaging:
                    messages.add_message(request, LOGIN_ERR, error, extra_tags="login_errors")
                # Reload homepage:
                return redirect("/")
            else:
                # If this is firing, it means errors returned, but they weren't expected.
                # Could mean someone is spoofing your URL request.
                print "Unexpected errors occurred."
                messages.add_message(request, LOGIN_ERR, "An unexpected error has occurred.", extra_tags="login_errors")
                return redirect("/") # Added for extra security to cover all cases.
        except KeyError:
            # If credentials are validated, set session, and load books page:
            print "User passed validation..."
            # Set session to validated User:
            print "Setting session data for logged in user..."
            request.session["user_id"] = validated["logged_in_user"].id
            # Load books page (books page):
            return redirect("/books")

    # If GET, reload index as this is an unexpected request:
    else:
        print "Unexpected errors occurred."
        messages.add_message(request, LOGIN_ERR, "An unexpected error has occurred.", extra_tags="login_errors")
        return redirect("/")

def logout(request):
    """Logs out current user."""

    # Try deleting session and send success message:
    try:
        # Deletes session:
        del request.session['user_id']
        # Adds success message:
        messages.add_message(request, LOGOUT_SUCC, "Successfully logged out.", extra_tags="logout_succ")
    except KeyError: # If `user_id` is not found pass
        pass

    # Return to index page:
    return redirect("/")

def get_dashboard_data(request):
    """
    Gets all book dashboard data.

    Data Fetched for Dashboard:
    - `current_user` - Gets current user.
    """

    # Validate user session prior to fetching book dashboard data:
    try:
        request.session["user_id"]
        print "User session validated."
        # Fetch book dashboard data for template:
        print "Fetching book dashboard data..."
        dashboard_data = helper.populate_dashboard_data(request.session["user_id"]) # custom module to get anything we need for dashboard
        # Load book dashboard and send dashboard data:
        return render(request, "reviewer/dashboard.html", dashboard_data)
    except KeyError:
        # If session object not found, load index:
        print "User session not validated."
        messages.add_message(request, LOGIN_ERR, "You must be logged in to view this page.", extra_tags="login_errors")
        return redirect("/")

def add_review(request):
    """Adds a book review."""

    # If POST, begin validation/creation of new book/review.
    if request.method == "POST":
        # Prepare data for creation:
        """
        Note: We will collect the author field (existing authors), and the new author field from the request.
        If a new author was submitted, we'll use that over the existing author.
        """
        review_data = {
            "book": request.POST["book"],
            "author": request.POST["author"],
            "add_author": request.POST["add_author"],
            "description": request.POST["description"],
            "rating": request.POST["rating"],
            "user_id": request.session["user_id"], # current session user
        }
        validated = Review.objects.validate(**review_data)
        try:
            # If errors, load add book page with errors:
            if len(validated["errors"]) > 0:
                print "Book review could not be created."
                # Generate Django errors:
                for error in validated["errors"]:
                    # Add error to Django's error messaging:
                    messages.add_message(request, REV_ERR, error, extra_tags="rev_errors")
                # Reload homepage:
                return redirect("/books/add")
            else:
                # If this is firing, it means errors returned, but they weren't expected.
                # Could mean someone is spoofing your URL request.
                print "Unexpected errors occurred."
                messages.add_message(request, REV_ERR, "An unexpected error has occurred.", extra_tags="rev_errors")
                return redirect("/books/add") # Added for extra security to cover all cases.
        except TypeError:
            # If review passed validation and creation, load show book page:
            print "Review passed validation..."
            # Load books page (books page):
            return redirect("/books/" + str(validated.book.id))

    else:
        # If GET, get all authors and load add book page:
        # Get all authors:
        all_authors = {
            "all_authors": Author.objects.all()
        }
        # Load add book page:
        return render(request, "reviewer/add_book_review.html", all_authors)


def book(request, id):
    """If GET, shows book and all reviews; If POST, create additional review for book."""


    book_data = {
        "book": Book.objects.get(id=id),
        "all_reviews": Review.objects.filter(book__id=id).order_by("-created_at"),
        "user_id": request.session["user_id"], # for deleting your own reviews
    }

    # If POST, create new book review:
    if request.method == "POST":
        # Prepare form data for model:
        review_data = {
            "description": request.POST["description"],
            "rating": request.POST["rating"],
            "book_id": id,
            "user_id": request.session["user_id"],
        }
        # Create new review for book:
        validated = Review.objects.add_review(**review_data)
        try:
            # If errors, load book page with errors:
            if len(validated["errors"]) > 0:
                print "Book review could not be created."
                # Generate Django errors:
                for error in validated["errors"]:
                    # Add error to Django's error messaging:
                    messages.add_message(request, REV_ERR, error, extra_tags="rev_errors")
                # Reload homepage:
                return redirect("/books/" + str(id))
            else:
                # If this is firing, it means errors returned, but they weren't expected.
                # Could mean someone is spoofing your URL request.
                print "Unexpected errors occurred."
                messages.add_message(request, REV_ERR, "An unexpected error has occurred.", extra_tags="rev_errors")
                return rredirect("/books/" + str(id)) # Added for extra security to cover all cases.
        except TypeError:
            # If review passed validation and creation, load book page:
            print "Review passed validation..."
            # Load books page (books page):
            return redirect("/books/" + str(validated.book.id))
    # If GET, load book page with book/review data:
    else:
        helper.make_stars(book_data["all_reviews"])
        # Load show book page with book/review data:
        return render(request, "reviewer/show_book.html", book_data)

def user(request, id):
    """Show user and user reviews."""

    # Get user data by id:
    user = {
        "user": User.objects.get(id=id),
        "total_reviews": User.objects.get(id=id).review_set.all().count(),
        "reviewed_books": Book.objects.filter(review__user__id=id).distinct(),
    }

    return render(request, "reviewer/show_user.html", user)

def destroy_review(request, id):
    """Destroys a review by ID from the database."""

    # Get Book that review belongs to:
    book = Book.objects.get(review__id=id)
    # Delete review:
    Review.objects.get(id=id).delete()
    # Reload book view page:
    return redirect("/books/" + str(book.id))
