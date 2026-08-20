from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def landing(request):
    return redirect("accounts:sign_up")


def sign_up(request):
    return HttpResponse("Sign up!")

