from django.contrib import auth
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from core.forms import CustomerForm
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

    context['page_title'] = 'Панель управления'
    #print(Services.objects.count())
    return render(request, "core/services_list.html", context)


def delete_account(request):
    return HttpResponse("account delete")


def create_account(request):
    return HttpResponse("Create")


@login_required(login_url='base_login')
def update_account(request, id, **args):
    info = get_object_or_404(CustomerInfo, pk=id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=info)
        if form.is_valid():
            info.description = request.POST.get('description')
            info.INN = request.POST.get('INN')
            info.phone_number = request.POST.get('phone_number')
            info.save()
            redirect('/', id=id)
    else:
        #info = CustomerInfo.objects.get(pk=id)
        form = CustomerForm(instance=info)
        return render(request, 'core/account_detail.html', {'form': form})


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
            login_error = 'Сожалеем, вы неправильно ввели логин или пароль'
            context = {'login_error': login_error}
            return render(request, 'core/base_login.html', context)
    else:
        return render(request, 'core/base_login.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
