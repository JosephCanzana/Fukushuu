from django.urls import path
from . import views

urlpatterns = [
    path("", views.account_landing, name="account_landing"),
    path("sign_up/", views.sign_up, name="sign_up"),
]