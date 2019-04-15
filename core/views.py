from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return render(request, "core/base.html")


def delete_account(request):
    return HttpResponse("account delete")


def create_account(request):
    return HttpResponse("Create")

def update_account(request, **args):
    return HttpResponse(args)