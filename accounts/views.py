from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def account_landing(request):
    return redirect("sign_up")


def sign_up(request):
    return HttpResponse("Sign up!")

