from __future__ import unicode_literals

from django.db import models
import re # regex
import bcrypt # grabs `bcrypt` module for encrypting and decrypting passwords

class UserManager(models.Manager):
    """
    Extends `Manager` methods to add validation and creation functions.

    Parameters:
    - `models.Manager` - Gives us access to the `Manager` method to which we
    append additional custom methods.

    Functions:
    - `register_validate(self, **kwargs)` - Accepts a dictionary list of
    registration form arguments. Either returns errors list if validation fails, or
    hashes password and returns the validated and newly created `User`.
    - `login_validate(self, **kwargs)` - Accepts a dictionary list of login
    form arguments. Either returns errors list if validation fails, or returns the
    validated retrieved user.
    """

    def register_validate(self, **kwargs):
        """
        Runs validations on new User.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of registration values from controller to be validated.

        Validations:
        - First Name - Required; No fewer than 2 characters; letters only
        - Last Name - Required; No fewer than 2 characters; letters only
        - Email - Required; Valid Format
        - No Existing User - Check by email
        - Password - Required; No fewer than 8 characters in length; matches Password Confirmation
        """

        # Create empty errors list, which we'll return to generate django messages back in views.py:
        errors = []

        #---------------------------#
        #-- FIRST_NAME/LAST_NAME: --#
        #---------------------------#
        # Check if first_name or last_name is less than 2 characters:
        if len(kwargs["first_name"]) < 2 or len(kwargs["last_name"]) < 2:
            # Add error to error's list:
            errors.append('First and last name are required must be at least 2 characters.')

        # Check if first_name or last_name contains letters only:
        alphachar_regex = re.compile(r'^[a-zA-Z]*$') # Create regex object
        # Test first_name and last_name against regex object:
        if not alphachar_regex.match(kwargs["first_name"]) or not alphachar_regex.match(kwargs["last_name"]):
            # Add error to error's list:
            errors.append('First and last name must be letters only.')

        #------------#
        #-- EMAIL: --#
        #------------#
        # Check if email field is empty:
        if len(kwargs["email"]) < 5:
            # Add error to error's list:
            errors.append('Email field is required.')

        # Note: The `else` statements below will only run if the above if statement passes.
        # This is to keep us from giving away too many errors when not quite yet necessary.
        else: # if longer than 5 char:
            # Check if email is in proper format:
            # Create regex object:
            email_regex = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
            if not email_regex.match(kwargs["email"]):
                # Add error to error's list:
                errors.append('Email format is invalid.')
            else: # If passes regex:
                #---------------#
                #-- EXISTING: --#
                #---------------#
                # Check for existing User via email:
                if len(User.objects.filter(email=kwargs["email"])) > 0:
                    # Add error to error's list:
                    errors.append('Email address already registered.')

        #---------------#
        #-- PASSWORD: --#
        #---------------#
        # Check if password is not less than 8 characters:
        if len(kwargs["password"]) < 8:
            # Add error to error's list:
            errors.append('Password fields are required and must be at least 8 characters.')
        # Otherwise check if it matches the confirmation. If it does, bcrpyt it and send it back.
        else:
            # The above else statement is so the code below only runs if the password
            # is more than 8 characters. Again, this is to prevent excessive errors.
            # Check if password matches confirmation password:
            if kwargs["password"] != kwargs["confirm_pwd"]:
                # Add error to error's list:
                errors.append('Password and confirmation password must match.')

        #------------------------------#
        #---- IF VALIDATION PASSES ----#
        #------------------------------#
        # If no validation errors, hash password, create user and send new user back:
        if len(errors) == 0:
            print "Registration data passed validation..."
            print "Hashing password..."
            # Hash Password:
            kwargs["password"] = bcrypt.hashpw(kwargs["password"].encode(), bcrypt.gensalt(14))
            print "Password hashed."
            print "Creating new user with data..."
            # Create new validated User:
            validated_user = {
                "logged_in_user": User(first_name=kwargs["first_name"], last_name=kwargs["last_name"], email=kwargs["email"], password=kwargs["password"])
            }
            # Save new User:
            validated_user["logged_in_user"].save()
            print "New `User` created:"
            print "{} {} | {} | {}".format(validated_user["logged_in_user"].first_name,validated_user["logged_in_user"].last_name, validated_user["logged_in_user"].email, validated_user["logged_in_user"].created_at)
            print "Logging user in..." # // Development Improvement Note: // Could assign Session here.
            # Send newly created validated User back:
            return validated_user
        #-----------------------------#
        #---- IF VALIDATION FAILS ----#
        #-----------------------------#
        # Else, if validation fails print errors to console and return errors:
        else:
            print "Errors validating User registration."
            for error in errors:
                print "Validation Error: ", error
            # Prepare data for `views.py`:
            errors = {
                "errors": errors,
            }
            return errors

    def login_validate(self, **kwargs):
        """
        Runs validations for User attempting to login.

        Parameters:
        - `self` - Instance to whom this method belongs.
        - `**kwargs` - Dictionary object of login values from controller to be validated.

        Validations:
        - All fields required.
        - Email retrieves existing User.
        - Password matches User's stored password (bcrypted).
        """

        # Create empty errors list, which we'll return to generate django messages back in views.py:
        errors = []

        #------------------#
        #--- ALL FIELDS ---#
        #------------------#
        # Check that all fields are required:
        if len(kwargs["email"]) < 5 or len(kwargs["password"]) < 8:
            # Add error to error's list:
            errors.append('All fields are required.')
        # If all fields are filled in:
        else:
            #------------------#
            #---- EXISTING ----#
            #------------------#
            # Try retrieving existing User:
            try:
                logged_in_user = User.objects.get(email=kwargs["email"])
                print "User found..."

                #------------------#
                #---- PASSWORD ----#
                #------------------#
                # Compare passwords with bcrypt:
                # Notes: We pass in our `kwargs['password']` chained to the `str.encode()` method so it's ready for bcrypt.
                # We could break this down into a separate variable, but instead we do it all at once for zen simplicity's sake.
                try:
                    if bcrypt.hashpw(kwargs["password"].encode(), logged_in_user.password.encode()) != logged_in_user.password:
                        # Add error to error's list:
                        errors.append('Login invalid.')
                except ValueError:
                    # This will only run if the user's stored DB password is unable to be used by bcrypt (meaning the created user's p/w was never hashed):
                    errors.append('This user is corrupt. Please contact the administrator.')

            except User.DoesNotExist:
                print "Error, User has not been found."
                # Add error to error's list:
                errors.append('Login invalid.')

        #------------------------------#
        #---- IF VALIDATION PASSES ----#
        #------------------------------#
        # If no validation errors, send back validated user:
        if len(errors) == 0:
            print "Login data passed validation..."
            print "Logging user in..." # // Development Improvement Note: // Could assign Session here.
            # Prepare data for Template:
            validated_user = {
                "logged_in_user": logged_in_user, # email of our retrieved `User` from above validations.
            }
            # Send back retrieved User:
            return validated_user
        # Else, if validation fails print errors to console and return errors:
        else:
            #-----------------------------#
            #---- IF VALIDATION FAILS ----#
            #-----------------------------#
            print "Errors validating User login."
            for error in errors:
                print "Validation Error: ", error
            # Prepare data for `views.py`:
            errors = {
                "errors": errors,
            }
            return errors

class ReviewManager(models.Manager):
    """
    Extends `Manager` methods to add validation and creation functions.

    Parameters:
    - `models.Manager` - Gives us access to the `Manager` method to which we
    append additional custom methods.

    Functions:
    - `validate(self, **kwargs)` - Accepts a dictionary list of
    book review form arguments. Either returns errors list if validation fails, or
    returns newly created book.
    """

    def validate(self, **kwargs):
        """
        Runs validations on new book review and creates new author if does not currently exist.

        Parameters:
        - `**kwargs` - a dictionary list of book review data for review creation.

        Validation overview notes:
        In a nutshell, there are several layers of validation and checking that is done below.
        Check if required fields submitted -- error if not.
        Check if new author was submitted:
        ---> If so, check that only first/last name are submitted. Note: Could change your `Author` model so only a single name field is provided, rather than first and last, to simplify. But for now this is OK.
        ---> Ensure name submitted, does not match an existing author. Send error if so.
        ---> If author is unique, then create new book and new author, assigning new author to book.
        If existing author detected:
        ---> Get author.
        If validations above pass:
        ---> Check if book title already exist for author.
        -------> If so, create new review for existing book.
        -------> Else, create new review for new book, and add new book to existing author.
        Return review if successful. Return errors if not.
        """

        # Create empty errors list, which we'll return to generate django messages back in views.py:
        errors = []

        #------------------#
        #---- REQUIRED ----#
        #------------------#
        # Check if required fields are empty:
        if len(kwargs["book"]) < 1 or len(kwargs["description"]) < 1:
            # Add error to error's list:
            errors.append('A book title and book review is required.')

            errors = {
                "errors": errors,
            }
            return errors

        # Check if less than 500 characters:
        if len(kwargs["description"]) > 500:
            errors.append('Review must be less than 500 characters.')

        # Check if less than 500 characters:
        if len(kwargs["book"]) > 100:
            errors.append('Title must be less than 100 characters.')

        #------------------------#
        #---- IF NEW AUTHOR  ----#
        #------------------------#
        # Check if custom add author form was filled out:
        if len(kwargs["add_author"]) > 0:
            # If add detected, split the string submitted into a first and last name (for object creation):
            print "Add new author detected..."
            author = kwargs["add_author"].split()
            print author

            #------------------------------------#
            #---- NEW AUTHOR FIRST/LAST ONLY ----#
            #------------------------------------#
            # Ensure that only a first and last name were submitted (no middle initials/no first names only):
            if len(author) > 2 or len(author) == 1:
                print "Error, Author name contains more than a first and last name."
                errors.append('New Author may contain a first and last name only. Middle names or initials are not allowed.')
            else:
                #-----------------------------------#
                #---- NEW AUTHOR MUST BE UNIQUE ----#
                #-----------------------------------#
                # If only first and last name provided, check if existing author:
                if len(Author.objects.filter(first_name=author[0], last_name=author[1])) < 1:
                    print "Author passed validation...no existing author detected..."
                    # Create new custom author (saving it in place of our kwargs["author"]):
                    kwargs["author"] = Author(first_name=author[0], last_name=author[1])
                    kwargs["author"].save()
                    # Create new book with new author:
                    new_author_book = Book(title=kwargs["book"], author=kwargs["author"])
                    new_author_book.save()
                else:
                    # If existing author detected, create error:
                    print "Error, Existing author detected, validation failed."
                    errors.append('This author already exists in the dropdown.')
        else:
            #----------------------------#
            #---- IF EXISTING AUTHOR ----#
            #----------------------------#
            # If no custom author submitted, continue:
            print "Existing author detected..."
            # Retrieve existing author and replace kwargs["author"] with full author object (will help in object creation):
            kwargs["author"] = Author.objects.get(id=kwargs["author"])
            print "Existing author has been retrieved..."

        #------------------------------#
        #---- IF VALIDATION PASSES ----#
        #------------------------------#
        # If no validation errors, begin review creation:
        if len(errors) == 0:
            print "Review passed initial validation..."

            # Check if book already exists for author -- if so create, review:
            print "Checking if book title already exists for author..."

            try:
                if Book.objects.get(title=kwargs["book"]) in kwargs["author"].book_set.all():
                    #----------------------------------------#
                    #---- EXISTING BOOK, EXISTING AUTHOR ----#
                    #----------------------------------------#
                    print "Book already exists for author..."
                    print "Adding review for existing book..."
                    # Create new review for existing book:
                    add_book_review = Review(description=kwargs["description"], user=User.objects.get(id=kwargs["user_id"]), book=Book.objects.get(title=kwargs["book"]), rating=kwargs["rating"])
                    add_book_review.save()
                    # Send back review for existing book:
                    return add_book_review
            except Book.DoesNotExist:
                #-----------------------------------#
                #---- NEW BOOK, EXISTING AUTHOR ----#
                #-----------------------------------#
                # If book does not exist for author, create book then create review:
                new_book = Book(title=kwargs["book"], author=kwargs["author"])
                new_book.save()
                # Create review & Save review:
                new_book_review = Review(description=kwargs["description"], user=User.objects.get(id=kwargs["user_id"]), book=new_book, rating=kwargs["rating"],)
                new_book_review.save()
                # Send back review for newly added book:
                return new_book_review
        else:
            #-----------------------------#
            #---- IF VALIDATION FAILS ----#
            #-----------------------------#
            # Else, if validation errors:
            # Return errors list:
            print "Errors validating book review."
            for error in errors:
                print "Validation Error: ", error
            # Prepare data for `views.py`:
            errors = {
                "errors": errors,
            }
            return errors

    def add_review(self, **kwargs):
        """Runs validations and creates new reviews from book page submission."""

        # Create empty errors list, which we'll return to generate django messages back in views.py:
        errors = []

        #------------------#
        #---- REQUIRED ----#
        #------------------#
        # Check if description field is empty:
        if len(kwargs["description"]) < 1:
            # Add error to error's list:
            errors.append('A review is required.')

        # Check if less than 500 characters:
        if len(kwargs["description"]) > 500:
            errors.append('Review must be less than 500 characters.')

        # If no errors:
        if len(errors) == 0:
            # Create new review for the book and send back:
            add_review = Review(description=kwargs["description"], user=User.objects.get(id=kwargs["user_id"]), book=Book.objects.get(id=kwargs["book_id"]), rating=kwargs["rating"])
            add_review.save()
            return add_review
        else:
            # Format for controller and send back errors:
            errors = {
                "errors": errors,
            }
            return errors



class User(models.Model):
    """
    Creates instances of a `User`.

    Parameters:
    -`models.Model` - Django's `models.Model` method allows us to create new models.
    """

    first_name = models.CharField(max_length=50) # CharField is field type for characters
    last_name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=22)
    created_at = models.DateTimeField(auto_now_add=True) # DateTimeField is field type for date and time
    updated_at = models.DateTimeField(auto_now=True) # note the `auto_now=True` parameter
    objects = UserManager() # Attaches `UserManager` methods to our `User.objects` object.

class Author(models.Model):
    """
    Creates instances of a `Author`.

    Parameters:
    -`models.Model` - Django's `models.Model` method allows us to create new models.
    """

    first_name = models.CharField(max_length=50) # CharField is field type for characters
    last_name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True) # DateTimeField is field type for date and time
    updated_at = models.DateTimeField(auto_now=True) # note the `auto_now=True` parameter

class Book(models.Model):
    """
    Creates instances of a `Book`.

    Parameters:
    -`models.Model` - Django's `models.Model` method allows us to create new models.
    """

    title = models.CharField(max_length=100) # CharField is field type for characters
    author = models.ForeignKey(Author, on_delete=models.CASCADE) # ties us into an author for the book. if author deleted, books delete too.
    created_at = models.DateTimeField(auto_now_add=True) # DateTimeField is field type for date and time
    updated_at = models.DateTimeField(auto_now=True) # note the `auto_now=True` parameter


class Review(models.Model):
    """
    Creates instances of a `Review`.

    Parameters:
    -`models.Model` - Django's `models.Model` method allows us to create new models.
    """

    description = models.CharField(max_length=500) # CharField is field type for characters
    user = models.ForeignKey(User, on_delete=models.CASCADE) # ties to user, if user deleted, deletes all user reviews
    book = models.ForeignKey(Book) # book for review
    rating = models.IntegerField() # user rating between 1-5
    created_at = models.DateTimeField(auto_now_add=True) # DateTimeField is field type for date and time
    updated_at = models.DateTimeField(auto_now=True) # note the `auto_now=True` parameter
    objects = ReviewManager() # Attaches 'ReviewManager' to `Review.objects` methods.
