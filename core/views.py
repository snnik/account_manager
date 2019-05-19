from django.views import View
from django.views.generic import DetailView, ListView
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import *
from .models import Customer, Service, Package, Protocol


#
class ObjectsLists(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    view_title = None
    page_title = None
    permission_required = ''

    def get_context_data(self, **kwargs):
            context = super(ObjectsLists, self).get_context_data(**kwargs)
            context['page_title'] = self.view_title
            context['view_title'] = self.view_title
            return context


class CustomerList(ObjectsLists):
    model = Customer
    view_title = 'Клиенты'
    page_title = ''
    permission_required = ('core.view_customer', 'auth.view_user')


class AccountList(ObjectsLists):
    model = User
    template_name = 'core/account_list.html'
    view_title = 'Accounts'
    page_title = ''
    permission_required = ('auth.view_user',)


class ServiceList(ObjectsLists):
    model = Service
    view_title = 'Service'
    page_title = 'Services'
    permission_required = ('core.view_service',)


class PackageList(ObjectsLists):
    model = Package
    view_title = 'Package'
    page_title = 'Packages'
    permission_required = ('core.view_package',)


class GroupList(ObjectsLists):
    model = Group
    template_name = 'core/group_list.html'
    view_title = 'Group'
    page_title = 'Groups'
    permission_required = ('auth.group_view',)


@login_required(login_url='base_login')
def index(request):
    page_context = {'page_title': 'Панель управления'}
    services = Service.objects.all()
    user = request.user
    if not (user.is_superuser or user.is_staff):
        customer = user.customer
        page_context['customer'] = customer

    shortcuts = set()

    for service in services:
        permission_name = service._meta.app_label + '.' + service.fk_permission.codename

        if user.has_perm(permission_name):
            shortcuts.add(service)

    page_context['shortcuts'] = shortcuts
    return render(request, "core/dashboard.html", page_context)


@login_required()
@permission_required('auth.add_user')
def create_user(request):
    page_context = {'page_title': 'Создание пользователя'}
    if request.method == 'POST':
        user_form = CreateUserForm(request.POST)
        try:
            if user_form.is_valid():
                if user_form.cleaned_data['password'] == user_form.cleaned_data['password1']:
                    user = User.objects.create_user(username=user_form.cleaned_data['username'],
                                                    password=user_form.cleaned_data['password'])
                    log = Protocol()
                    log.save(username=request.user.username,
                             table='auth_user',
                             action='add',
                             obj=str(user),
                             obj_id=user.pk)
                    # return redirect('user_update', user_id=user.pk)
                else:
                    user_form.add_error('password1', 'Пароли не совпадают')
        except Exception as e:
            user_form.add_error('non_field_errors'.upper(), str(e))
            log = Protocol()
            log.save(username=request.user.username,
                     table='auth_user',
                     action='add',
                     obj=str(user),
                     obj_id=user.pk,
                     error=str(e))
    else:
        user_form = CreateUserForm()
    page_context['form'] = user_form
    return render(request, 'core/account_detail.html', page_context)


@login_required()
@permission_required(('auth.change_user', 'auth.view_user'))
def update_user(request, user_id):
    pass


@login_required()
@permission_required('auth.delete_user')
def delete_user(request, user_id):
    pass


@login_required(login_url='base_login')
@permission_required(('core.add_service', 'auth.add_permission'))
def create_service(request):
    page_context = {'page_title': 'Создание сервиса'}
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.save(username=request.user)
    else:
        form = ServiceForm()
    page_context['form'] = form
    return render(request, 'core/service_form.html', page_context)


@login_required(login_url='base_login')
def update_service(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    page_context = {'page_title': 'Изменение сервиса'}

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save(commit=False)
            service.save(username=request.user)
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
    return render(request, 'core/package_list.html', page_context)


@login_required()
def create_package(request):
    page_context = {'page_title': 'Создание пакета услуг'}

    if request.method == 'POST':
        form = PackageForm(request.POST)
        f_group = GroupForm(request.POST)
        if form.is_valid() and f_group.is_valid():
            package = form.save(commit=False)
            package.save(username=request.user, permissions=f_group.cleaned_data['permissions'])
            return redirect('package_update', sp_id=package.pk)
    else:
        f_group = GroupForm()
        form = PackageForm()

    page_context['form'] = form
    page_context['group'] = f_group
    return render(request, 'core/package_form.html', page_context)


@login_required()
def delete_package(request, sp_id):
    package = get_object_or_404(Package, pk=sp_id)
    group = package.group
    group.delete()
    return redirect('package_list')


@login_required()
def update_package(request, sp_id):
    package = get_object_or_404(Package, pk=sp_id)
    page_context = {'page_title': 'Пакет услуг ' + str(package.description) + ' : ' + str(package.pk)}

    if request.method == 'POST':
        package_form = PackageForm(request.POST, instance=package)
        group_form = GroupForm(request.POST, instance=package.group)
        if package_form.is_valid() and group_form.is_valid():
            group = group_form.save(commit=False)
            pkg = package_form.save(commit=False)
            pkg.save(username=request.user,
                     group=group.name,
                     permissions=group_form.cleaned_data['permissions'])
    else:
        package_form = PackageForm(instance=package)
        group_form = GroupForm(instance=package.group)

    page_context['form'] = package_form
    page_context['group'] = group_form
    return render(request, 'core/package_form.html', page_context)


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
@permission_required(('core.add_customer', 'auth.add_user'))
def create_account(request):
    page_context = {'page_title': 'Создание аккаунта'}
    password = None
    login = None

    if request.method == 'POST':
        form = CustomerForm(request.POST)
        account_form = AccountForm(request.POST)
        if form.is_valid() and account_form.is_valid():
            customer = form.save(commit=False)
            groups = account_form.cleaned_data['groups']
            login, password = customer.save(username=request.user, groups=account_form.cleaned_data['groups'])
    else:
        form = CustomerForm()
        account_form = AccountForm()

    page_context['form'] = form
    page_context['account_form'] = account_form
    page_context['password'] = password
    page_context['login'] = login

    return render(request, 'core/customer_detail.html', page_context)


@login_required(login_url='base_login')
def update_account(request, customer_id):
    context = {'page_title': 'изменение аккаунта'}
    customer = get_object_or_404(Customer, pk=customer_id, customer__is_active=True)
    user = customer.customer

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        account_form = AccountForm(request.POST, instance=user)
        if form.is_valid() and account_form.is_valid():
            customer.save(username=request.user, groups=account_form.cleaned_data['groups'])
    else:
        form = CustomerForm(instance=customer)
        account_form = AccountForm(instance=user)

    context['form'] = form
    context['account_form'] = account_form
    return render(request, 'core/customer_detail.html', context)


@login_required(login_url='base_login')
@permission_required(('core.change_customer', 'auth.change_user'))
def account_detail(request, customer_id, **kwargs):
    context = {'page_title': 'изменение аккаунта'}
    account = get_object_or_404(Customer, id=customer_id)
    user = account.customer

    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=account)
        account_form = AccountForm(request.POST, instance=user)
        if form.is_valid() and account_form.is_valid():
            account.save(username=request.user, groups=account_form.cleaned_data['groups'])
    else:
        form = CustomerForm(instance=account)
        account_form = AccountForm(instance=user)

    context['form'] = form
    context['account_form'] = account_form
    return render(request, 'core/customer_detail.html', context)


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


@login_required(login_url='base_login')
def password_change(reguest):
    return HttpResponse('Pass change')


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
