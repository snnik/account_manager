from django.contrib import auth
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from core.forms import CustomerForm, AccountForm
from .models import *
from .utils import *


# Create your views here.
@login_required(login_url='base_login')
def index(request):
    context = {}

    context['users'] = User.objects.all()
    return render(request, "core/account_list.html", context)


@login_required(login_url='base_login')
def services_list(request):
    context = {'page_title': 'Панель управления'}

    return render(request, "core/services_list.html", context)


def delete_account(request):
    return HttpResponse("account delete")


def create_account(request):
    return HttpResponse("Create")


@login_required(login_url='base_login')
def update_account(request, id, **args):
    errors = ''
    info = get_object_or_404(CustomerInfo, pk=id)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=info)
        if form.is_valid():
            info.description = form.cleaned_data['description']
            info.INN = form.cleaned_data['INN']
            info.KPP = form.cleaned_data['KPP']
            info.legal_address = form.cleaned_data['legal_address']
            info.postal_address = form.cleaned_data['postal_address']
            info.phone_number = form.cleaned_data['phone_number']
            info.email_address = form.cleaned_data['email_address']
            info.customer = form.cleaned_data['customer']
            info.save()
            return redirect('update-account', id=id)
        else:
            errors = form.errors

    context = {}
    form = CustomerForm(instance=info)
    context['form'] = form

    if errors:
        context['error_list'] = errors

    return render(request, 'core/account_detail.html', context)


@login_required(login_url='base_login')
def account_detail(request, id, **args):
    errors = ''
    account = get_object_or_404(User, id=id)
    if request.method == 'POST':
        form =  AccountForm(request.POST, instance=account)
        if form.is_valid():
            account.username = form.cleaned_data['username']
            account.save()
            return redirect('account-detail', id=id)
        else:
            errors = form.errors

    context = {}
    form = AccountForm(instance=account)
    context['form'] = form

    if errors:
        context['error_list'] = errors

    return render(request, 'core/account_detail.html', context)


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
