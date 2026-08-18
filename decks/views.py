from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def deck_landing(request):
    return HttpResponse("This is decks!")