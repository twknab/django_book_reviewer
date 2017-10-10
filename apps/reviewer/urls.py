"""Sets up URL files for all applications in this project."""

from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index), # load login/registration page
    url(r'^login$', views.login), # validate and login a user
    url(r'^logout$', views.logout), # logout a user
    url(r'^books$', views.get_dashboard_data), # fetch book dashboard data and load dashboard
    url(r'^books/add$', views.add_review), # show add book review form, or add a book review
    url(r'^books/(?P<id>\d*)$', views.book), # show book and reviews, or create new book
    url(r'^users/(?P<id>\d*)$', views.user), # show user and reviews
    url(r'^delete/(?P<id>\d*)$', views.destroy_review), # destroy a review
]
