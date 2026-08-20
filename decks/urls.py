from django.urls import path
from . import views

app_name = "decks"

urlpatterns = [
    path("", views.deck_landing, name="deck_landing"),
]