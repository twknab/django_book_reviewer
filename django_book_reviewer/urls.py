"""Sets up URL configurations for each application belonging to this project."""
from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include("apps.reviewer.urls")),
]
