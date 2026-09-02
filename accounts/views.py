from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import auth
from .forms import SignUpForm, LoginForm
from accounts.models import User

# Create your views here.
def landing(request):
    return redirect("accounts:sign_up")


def sign_up(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            return HttpResponse(f"Account created for {user.username}")
        else:
            return render(request, "accounts/sign_up.html", {"form": form})
    else:
        return render(request, "accounts/sign_up.html")

def login(request):
    if request.method == "POST":
        form = LoginForm(request.POST)

        if form.is_valid():
            auth.login(request, form.cleaned_data["user"])
            return render(request, "decks/dashboard.html")
        else:
            return render(request, "accounts/login.html")
        
    else:
        return render(request, "accounts/login.html")