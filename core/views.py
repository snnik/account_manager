from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import auth
from core.forms import CustomerForm, ServiceForm, PackageForm
from .models import *


# Create your views here.
@login_required(login_url='base_login')
def index(request):
    return render(request, "core/dashboard.html", {'page_title': 'Панель управления'})


@login_required(login_url='base_login')
def accounts_list(request):
    page_context = {}
    page_context['page_title'] = 'Аккаунты'
    page_context['customer'] = Customer.objects.all()
    return render(request, 'core/account_list.html', context=page_context)


@login_required(login_url='base_login')
def services_list(request):
    context = {'page_title': 'Сервисы'}
    services = Service.objects.all()
    context['services'] = services
    return render(request, "core/services_list.html", context)


@login_required()
def create_service(request):
    page_context = {'page_title': 'Создание сервиса'}
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = ServiceForm()
    page_context['form'] = form
    return render(request, 'core/service_form.html', page_context)


@login_required()
def update_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    page_context = {'page_title': 'Изменение сервиса'}

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
    else:
        form = ServiceForm(instance=service)

    page_context['form'] = form
    return render(request, 'core/service_form.html', page_context)


@login_required()
def delete_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if service:
        service.delete()
    return redirect('services_list')


@login_required()
def list_package(request):
    packages = Package.objects.all()
    page_context = {'page_title': 'Список пакетов услуг', 'packages': packages}
    return render(request, 'core/packages_list.html', page_context)


@login_required()
def create_package(request):
    page_context = {'page_title': 'Создание пакета услуг'}
    if request.method == 'POST':
        form = PackageForm(request.POST)
        if form.is_valid():
            form.save()
    else:
        form = PackageForm()

    page_context['form'] = form
    return render(request, 'core/package_form.html', page_context)


@login_required()
def delete_package(request, sp_id):
    return HttpResponse('delete package' + str(sp_id))


@login_required()
def update_package(request, sp_id):
    return HttpResponse('update package' + str(sp_id))


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
