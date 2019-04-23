from django.shortcuts import render
from django.http import HttpResponse
from .models import *


# Create your views here.
def index(request):
    #print(Services.objects.count())
    return render(request, "core/account_list.html", context={'services': Services.objects.all()})


def delete_account(request):
    return HttpResponse("account delete")


def create_account(request):
    return HttpResponse("Create")


def update_account(request, **args):
    return HttpResponse(args)