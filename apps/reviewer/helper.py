"""Helper module for gathering Dashboard or other Show data."""

from models import User, Author, Book, Review # gives us access to all models
from django.db.models import Count

def create_authors():
    """Creates a few authors for initial add review page if there aren't any."""

    # If no authors, create 3:

    all_authors = Author.objects.all()
    print "Current # of authors: {}".format(len(all_authors))

    if len(Author.objects.all()) < 1:
        print "No authors...creating some now..."
        a1 = Author(first_name="Stephen", last_name="King")
        a1.save()
        a2 = Author(first_name="Ray", last_name="Bradbury")
        a2.save()
        a3 = Author(first_name="Aldous", last_name="Huxley")
        a3.save()
    else:
        print "Authors detected. Creation aborted."
        pass

def make_stars(reviews_list):
    """
    Converts rating to generated dictionary with list of number of full, half and empty stars.

    Parameters:
    - `reviews_list` - List of Review objects, of which to generate stars for.
    """

    # Iterate through list:
    for review in reviews_list:
        # Create a new property for the review which holds a list to store stars/empty stars:
        review.stars = []
        review.empty = []
        for x in range (0, review.rating):
            # Starting at 0 and stopping at the review.rating, add the star to the array:
            # Note: We will iterate through the array on the template to display stars.
            review.stars.append(x)
        empty_stars = 5 - len(review.stars)
        print empty_stars
        for y in range (0, empty_stars):
            review.empty.append(y)


def populate_dashboard_data(id):
    """
    Create dictionary for Dashboard Template.

    Parameters:
    - `id` - Session user id of currently logged in user.
    """

    # Create any authors if there aren't any (to genereate data for add review form)
    create_authors()

    book = Book.objects.filter(title="Test!")
    print book

    # Prepare data for Dashboard by running functions above, which collect the data we need:
    dashboard_data = {
        "current_user": User.objects.get(id=id), # Gets current session user
        "3_recent_reviews": Review.objects.all().order_by("-created_at")[:3], # Gets latest 3 reviews
        "all_books": Book.objects.filter(review__gte=1).distinct(), # Gets all distinct books with a review
    }

    # Create star rating for top 3 reviews:
    make_stars(dashboard_data["3_recent_reviews"])

    # Send back dashboard data which contains most recent and popular secrets with like counts, and the logged in user:
    return dashboard_data
