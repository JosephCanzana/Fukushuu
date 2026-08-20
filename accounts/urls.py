from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("sign_up/", views.sign_up, name="sign_up"),
]