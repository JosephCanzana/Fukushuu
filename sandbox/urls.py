from django.urls import path
from . import views

urlpatterns = [
    path("", views.test_page, name="sandbox-test"),
    path("test_response/", views.test_response, name="response-test"),
]