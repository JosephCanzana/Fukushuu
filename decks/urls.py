from django.urls import path
from . import views

urlpatterns = [
    path("", views.deck_landing, name="deck_landing"),
]