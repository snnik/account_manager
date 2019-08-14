from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.urls import reverse
from django.conf import settings
from core.forms import *
from core.mixins import ListViewMixin
from core.mixins import UpdateFormMixin
from core.mixins import CreateFormMixin
from core.mixins import DeleteFormMixin
from .models import Customer, Service, Package
from django.contrib.admin.models import ADDITION, DELETION, CHANGE, LogEntry
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver


def write_log(usr, obj, flag):
    LogEntry.objects.log_action(
        user_id=usr.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=flag,
        change_message=obj
    )

# Customer block
@login_required(login_url=reverse_lazy('base_login'))
@permission_required(('core.change_customer', 'auth.change_user'))
def deactivate_account(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.deactivate()
    return redirect('accounts_list')


@login_required(login_url=reverse_lazy('base_login'))
@permission_required(('core.change_customer', 'auth.change_user'))
def activate_account(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    customer.activate()
    return redirect('accounts_list')


class CustomerList(ListViewMixin):
    model = Customer
    view_title = 'Клиенты'
    page_title = ''
    heads = ('ID', 'Логин', 'Наименование', 'Последний логин',)
    permission_required = ('core.view_customer', 'auth.view_user')
    create_uri = 'account_create'


class CreateCustomer(CreateFormMixin):
    page_title = 'Создание аккаунта'
    form_title = 'Создание аккаунта'
    permission_required = ('core.add_customer', 'auth.add_user')
    form_class = CustomerForm
    success_url = None
    template_name = 'core/customer_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['group_form'] = GroupSelectForm()
        kwargs['group_form'].fields['groups'].queryset = Group.objects.filter(package__isnull=False)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        group_form = GroupSelectForm(self.request.POST)

        if not group_form.is_valid():
            return self.form_invalid((form, group_form))

        customer = form.save(commit=False)
        try:
            customer.create_user()
            write_log(self.request.user, customer.account, ADDITION)
            send_mail('Пароль',
                      'Учетные данные:' +
                      str(customer.account_login) +
                      ' ' +
                      str(customer.account_password),
                      'snnik1@gmail.com',
                      ('snnik@live.com',)
                      )
            customer.changed_group(group_form.cleaned_data['groups'])
            write_log(self.request.user, customer.account, CHANGE)
            customer.save()
            self.object = customer
        except Error as e:
            # Signals/log
            return self.form_invalid((form, group_form,))
        return redirect(self.get_success_url())


class UpdateCustomer(UpdateFormMixin):

    page_title = 'Создание аккаунта'
    form_title = 'Создание аккаунта'
    permission_required = ('core.change_customer', 'auth.change_user',)
    form_class = CustomerForm
    model = Customer
    success_url = None
    template_name = 'core/customer_detail.html'

    def get_context_data(self, **kwargs):
        kwargs['id'] = self.object.pk
        kwargs['group_form'] = GroupSelectForm(instance=self.object.account)
        kwargs['group_form'].fields['groups'].queryset = Group.objects.filter(package__isnull=False)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        group_form = GroupSelectForm(self.request.POST, instance=self.object.account)
        if not group_form.is_valid():
            return self.form_invalid((form, group_form))

        customer = form.save(commit=False)
        try:
            customer.changed_group(group_form.cleaned_data['groups'])
            customer.save()
            self.object = customer
            write_log(self.request.user, customer, CHANGE)
        except Error as e:
            # log
            return self.form_invalid((form, group_form))
        return redirect(self.get_success_url())



# Accounts block
@login_required(login_url=reverse_lazy('base_login'))
@permission_required('auth.add_user')
def create_user(request):
    page_context = {'page_title': 'Создание пользователя'}
    if request.method == 'POST':
        account_form = AccountCreationForm(request.POST)
        if account_form.is_valid():
            account = account_form.account_create(user_id=request.user.pk)
            if not account_form.errors:
                return redirect('user_update', user_id=account.pk)
    else:
        account_form = AccountCreationForm()
    page_context['form'] = account_form
    return render(request, 'core/account_detail.html', page_context)


@login_required(login_url=reverse_lazy('base_login'))
@permission_required(('auth.change_user', 'auth.view_user'))
def update_user(request, user_id):
    page_context = {}
    account = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        account_form = AccountChangeForm(request.POST, instance=account)
        if account_form.is_valid():
            account_form.save(user_id=request.user.pk)
    else:
        account_form = AccountChangeForm(instance=account)
    page_context['page_title'] = 'Изменение пользователя: ' + str(account) + ' ID: ' + str(account.pk)
    page_context['account_id'] = user_id
    page_context['form'] = account_form
    return render(request, 'core/account_detail.html', page_context)


@login_required(login_url=reverse_lazy('base_login'))
@permission_required('auth.delete_user')
def delete_user(request, user_id):
    # Создать форму для проверки связанных объектов, и подтверждения их удаления
    account = get_object_or_404(User, pk=user_id)
    if account:
        account.delete()
    return redirect('user_list')


class AccountList(ListViewMixin):
    model = User
    template_name = 'core/account_list.html'
    heads = ('ID', 'Логин', 'Имя пользователя',)
    view_title = 'Accounts'
    page_title = ''
    permission_required = ('auth.view_user',)
    create_uri = 'user_create'


# Services section

class ServiceList(ListViewMixin):
    model = Service
    heads = ('id', 'Наименование',)
    view_title = 'Service'
    page_title = 'Services'
    permission_required = ('core.view_service',)
    create_uri = 'service_create'


class ServiceCreate(CreateFormMixin):
    form_title = 'Create service'
    page_title = 'service'
    template_name = 'core/service_form.html'
    permission_required = ('core.add_service', 'auth.add_permission')
    form_class = ServiceForm
    success_url = None

    def form_valid(self, form):
        service = form.save(commit=False)
        service.shortcut_path = form.cleaned_data['shortcut_path']
        try:
            service.save()
            write_log(self.request.user, service.fk_permission, ADDITION)
            write_log(self.request.user, service, ADDITION)
            self.object = service
        except Exception as e:
            form.form_error.append(str(e))
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class ServiceUpdate(UpdateFormMixin):
    form_title = 'Update service'
    page_title = 'service'
    template_name = 'core/service_form.html'
    permission_required = ('core.change_service',)
    form_class = ServiceForm
    model = Service

    def form_valid(self, form):
        service = form.save(commit=False)
        service.shortcut_path = form.cleaned_data['shortcut_path']
        try:
            service.save()
            self.object = service
            write_log(self.request.user, service, CHANGE)
        except Exception as e:
            form.form_error.append(str(e))
            return self.form_invalid(form)
        return redirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        kwargs['pk'] = self.object.pk
        return super().get_context_data(**kwargs)


class ServiceDelete(DeleteFormMixin):
    form_title = 'Delete Service'
    page_title = 'service'
    permission_required = ('core.delete_service',)
    model = Service

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        write_log(self.request.user, instance, DELETION)
        write_log(self.request.user, instance.fk_permission, DELETION)
        return super().delete(request, args, kwargs)


# Packages sections

class PackageList(ListViewMixin):
    model = Package
    heads = ('id', 'Наименование', )
    view_title = 'Package'
    page_title = 'Packages'
    permission_required = ('core.view_package',)
    create_uri = 'package_create'


class PackageCreate(CreateFormMixin):
    form_title = 'Package create'
    page_title = 'Package'
    template_name = 'core/package_form.html'
    permission_required = ('core.add_package', 'auth.add_group', )
    form_class = PackageForm
    success_url = None

    def get_context_data(self, **kwargs):
        if 'group' not in kwargs:
            kwargs['group'] = GroupForm()

        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form_group = GroupForm(self.request.POST)
        if not form_group.is_valid():
            group = form_group
            return self.form_invalid((form, group))

        package = form.save(commit=False)
        try:
            package.set_group_fk(group_name=form.cleaned_data['description'])
            package.set_permissions(permissions=form_group.cleaned_data['permissions'])
            package.save()
            self.object = package
            write_log(self.request.user, package, ADDITION)
        except Error as e:
            form.form_error.append(str(e))
            return self.form_invalid()
        return redirect(self.get_success_url())


class PackageUpdate(UpdateFormMixin):
    form_title = 'Редактирование пакета услуг'
    page_title = 'Редактирование пакета услуг'
    permission_required = ('core.add_package', 'auth.add_group',)
    template_name = 'core/package_form.html'
    form_class = PackageForm
    model = Package
    success_url = None

    def get_context_data(self, **kwargs):
        obj = self.get_object()
        kwargs['pk'] = obj.pk
        kwargs['group'] = GroupForm(instance=obj.group)
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form_group = GroupForm(self.request.POST, instance=self.object.group)
        if not form_group.is_valid():
            group = form_group
            return self.form_invalid((form, group))

        package = form.save(commit=False)
        try:
            package.set_permissions(permissions=form_group.cleaned_data['permissions'])
            package.save()
            write_log(self.request.user, package, CHANGE)
            self.object = package
        except Error as e:
            form.form_error.append(str(e))
            return self.form_invalid(form)
        return redirect(self.get_success_url())


class PackageDelete(DeleteFormMixin):
    permission_required = ('core.delete_package', 'auth.delete_group')
    model = Package

    def get_context_data(self, **kwargs):
        kwargs['pk'] = self.object.id
        kwargs['page_title'] = 'Удаление пакета: ' + str(self.object)
        kwargs['foreign_object'] = (self.object.group, )
        return super().get_context_data(**kwargs)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        write_log(self.request.user, instance, DELETION)
        write_log(self.request.user, instance.group, DELETION)
        return super().delete(request, args, kwargs)


# Groups management sections. Admin privileges or auth.group_.... permissions required.

class GroupList(ListViewMixin):
    model = Group
    template_name = 'core/group_list.html'
    heads = ('id', 'Наименование', )
    view_title = 'Group'
    page_title = 'Groups'
    permission_required = ('auth.group_view',)
    create_uri = 'group_create'


@login_required(login_url=reverse_lazy('base_login'))
def profile(request):
    if request.user.is_staff:
        p = get_object_or_404(User, pk=request.user.pk)
        g = p.groups.all()
        form = ProfileForm(instance=p)
        template = 'core/profile.html'
    else:
        p = get_object_or_404(Customer, pk=request.user.customer.pk)
        template = 'core/customer_profile.html'
    return render(request, template, {'profile': p, 'groups': g, 'form': form})


@login_required(login_url=reverse_lazy('base_login'))
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


@login_required(login_url=reverse_lazy('base_login'))
@permission_required('auth.add_group')
def group_view(request, group_id=None):
    page_context = {}
    if request.method == 'POST':
        if group_id:
            group = get_object_or_404(Group, pk=group_id)
            group_form = GroupCreateForm(request.POST, instance=group)
        else:
            group_form = GroupCreateForm(request.POST)
        if group_form.is_valid:
            group_form.save(user_id=request.user.pk)
    else:
        if group_id:
            group = get_object_or_404(Group, pk=group_id)
            group_form = GroupCreateForm(instance=group)
            page_context['page_title'] = 'Редактирование группы'
        else:
            group_form = GroupCreateForm()
            page_context['page_title'] = 'Создание группы'
    page_context['form'] = group_form
    return render(request, 'core/group_detail.html', page_context)


def login(request):
    context = {}
    request.session.set_expiry(settings.PASSWORD_BLOCK_SESSION)
    incorrect = request.session.get('incorrect', 0)
    if incorrect >= 5:
        login_error = 'Работа запрещена!'
        context = {'login_error': login_error}
    else:
        if request.method == 'POST':
            username = request.POST.get('username', '')
            password = request.POST.get('password', '')
            user = auth.authenticate(username=username, password=password)
            if user and not user.last_login:
                change_password = True
            else:
                change_password = False
            if user is not None:
                auth.login(request, user)
                request.session.set_expiry(0)
                if change_password:
                    return redirect(reverse('change_pass'))
                else:
                    return HttpResponseRedirect('/')
            else:
                request.session['incorrect'] = incorrect + 1
                login_error = 'Сожалеем, вы неправильно ввели логин или пароль. Осталось попыток:' + str(5-incorrect)
                context = {'login_error': login_error}
    return render(request, 'core/base_login.html', context)


def password_change(request):
    context = {}
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            form.save(request.user)
            return HttpResponseRedirect('/')
    else:
        form = ChangePasswordForm()
    context['form'] = form
    return render(request, 'core/password_change.html', context)


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
