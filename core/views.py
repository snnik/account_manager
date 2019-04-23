from django.contrib import auth
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from .models import *


# Create your views here.
@login_required(login_url='base_login')
def index(request):
    context = {}
    context['contract'] = Contract.objects.all()
    context['users'] = User.objects.all()
    return render(request, "core/account_list.html", context)


@login_required(login_url='base_login')
def services_list(request):
    context = {}
    context['services'] = Services.objects.all()
    context['username'] = auth.get_user(request).username
    context['superuser'] = auth.get_user(request).is_superuser
    context['page_title'] = 'Панель управления'
    #print(Services.objects.count())
    return render(request, "core/services_list.html", context)


def delete_account(request):
    return HttpResponse("account delete")


def create_account(request):
    return HttpResponse("Create")


def update_account(request, **args):
    return HttpResponse(args)


def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponseRedirect('/')
        else:
            login_error = 'User not exist'
            context = {'login_error': login_error}
            return render(request, 'core/base_login.html', context)
    else:
        return render(request, 'core/base_login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
