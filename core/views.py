from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth
from core.forms import CustomerForm, ServiceForm
from .models import *


# Create your views here.
@login_required(login_url='base_login')
def index(request):
    return render(request, "core/dashboard.html")


@login_required(login_url='base_login')
def accounts_list(request):
    context = {}
    context['customer'] = Customer.objects.all()
    return render(request, 'core/account_list.html', context)


@login_required(login_url='base_login')
def services_list(request):
    context = {'page_title': 'Панель управления'}
    services = Service.objects.all()
    context['services'] = services
    return render(request, "core/services_list.html", context)


@login_required()
def create_service(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ServiceForm()
    return render(request, 'core/service_form.html', {'form': form})


@login_required()
def update_service(request, service_id):
    return HttpResponse(service_id)


@login_required()
def delete_service(request, service_id):
    return HttpResponse(service_id)


@login_required(login_url='base_login')
def deactivate_account(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.deactivate()
    return redirect('accounts_list')


@login_required(login_url='base_login')
def activate_account(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.activate()
    return redirect('accounts_list')


@login_required(login_url='base_login')
def create_account(request):

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts_list')
    else:
        form = CustomerForm()

    return render(request, 'core/account_detail.html', {'form': form})


@login_required(login_url='base_login')
def update_account(request, customer_id):
    errors = {}
    customer = get_object_or_404(Customer, pk=customer_id, customer__is_active=True)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer.save(username=request.user)
            return redirect('account_update', id=customer_id, customer__is_active=True)
        else:
            errors = form.errors

    context = {}
    form = CustomerForm(instance=customer)
    context['form'] = form

    if errors:
        context['error_list'] = errors

    return render(request, 'core/account_detail.html', context)


@login_required(login_url='base_login')
@permission_required('core.change_customer')
def account_detail(request, customer_id, password=None, **kwargs):
    account = get_object_or_404(Customer, id=customer_id)
    usr = request.user
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=account)
        if form.is_valid():
            password = account.save(username=usr.username)

            if password:
                return redirect('account_detail', customer_id=customer_id, password=password)
            else:
                return redirect('account_detail', customer_id=customer_id)
    else:
        form = CustomerForm(instance=account)

    return render(request, 'core/account_detail.html', {'form': form, 'password': password})


def login(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            if user.last_login:
                return HttpResponseRedirect('/')
            # else:
            #     return HttpResponseRedirect(reverse('passchange'))
        else:
            login_error = 'Сожалеем, вы неправильно ввели логин или пароль'
            context = {'login_error': login_error}
            return render(request, 'core/base_login.html', context)
    else:
        return render(request, 'core/base_login.html', context)


@login_required(login_url='base_login')
def password_change(reguest):
    return HttpResponse('Pass change')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
