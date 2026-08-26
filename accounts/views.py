from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def landing(request):
    return redirect("accounts:sign_up")


def sign_up(request):
    if request == "POST":
        # Here you can print the request data to check if it's being submitted correctly
        print(request.POST)
        
        # You can also return a simple HTTP response with a success message
        return HttpResponse('Form submitted successfully', status=200)

    return render(request, "accounts/sign_up.html")

