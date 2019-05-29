from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, View
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import models
from django import forms
from django.contrib.admin.models import ADDITION, LogEntry
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import CreateUserForm, ContentType, CustomerForm, AccountForm
from core.models import Customer


class FormObject(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission = None
    page_title = None
    form_title = None
    permission_required = ()
    err_msg = None

    def get_form_context(self):
        pass

    def set_form_context(self):
        pass

    def get(self):
        pass

    def post(self, form):
        if self.err_msg:
            form.add_error(None, str(self.err_msg))
            return self.form_invalid(form)
        else:
            return redirect(self.success_url)


# Секция создание записей
class ObjectCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    permission = None
    page_title = None
    form_title = None
    permission_required = ()
    err_msg = None

    def object_create(self, form):
        pass

    def form_valid(self, form):
        self.object_create(form)
        if self.err_msg:
            form.add_error(None, str(self.err_msg))
            return self.form_invalid(form)
        else:
            return redirect(self.success_url)


class AccountCreate(ObjectCreate):
    form_class = CreateUserForm
    template_name = 'core/account_detail.html'
    success_url = reverse_lazy('user_list')

    def object_create(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        try:
            obj = User.objects.create_user(username=username, password=password)

            LogEntry.objects.log_action(
                user_id=self.request.user.id,
                content_type_id=ContentType.objects.get_for_model(self.form_class.Meta.model).pk,
                object_id=obj.pk,
                object_repr=repr(obj),
                action_flag=ADDITION
            )

        except Exception as e:
            self.err_msg = e


class CustomerCreate(View):
    form_class = {'customer_form': CustomerForm,
                  'account_form': AccountForm}
    model = Customer
    template_name = 'core/customer_detail.html'
    success_url = reverse_lazy('accounts_list')
    password = None
    login = None
    page_title = ''
    err_msg = None

    # def object_create(self, form):
    #     pass
    #
    # def get_context_data(self, **kwargs):
    #     context = super(CustomerCreate, self).get_context_data(**kwargs)
    #     context['account_form'] = AccountForm()
    #     return context
    def get_object_data(self, id):
        model_object = {'customer_form': get_object_or_404(self.model, pk=id), }
        model_object['account_form'] = model_object['customer_form'].customer
        return self.init_form(model_object)

    def init_form(self, object):
        result_dict = {}
        if object:
            for key, form in self.form_class.items():
                if isinstance(object[key], models.Model):
                    result_dict[key] = form(instance=object[key])
                if isinstance(object[key], forms.Form):
                    result_dict[key] = object[key]
        else:
            for key, form in self.form_class.items():
                result_dict[key] = form()
        return result_dict

    def set_form_context(self, **kwargs):
        context = {}
        id = kwargs.get('pk') or kwargs.get('id')

        if id and not self.err_msg:
            context = self.get_object_data(id=id)
        else:
            context = self.init_form(kwargs.get('forms'))

        if self.page_title:
            context['page_title'] = self.page_title
        if self.login:
            context['login'] = self.login
        if self.password:
            context['password'] = self.password

        return context

    def get_form_context(self, request, pk=None):
        customer_form = self.form_class['customer_form'](request.POST)
        account_form = self.form_class['account_form'](request.POST)
        if customer_form.is_valid() and account_form.is_valid():
            model_object = customer_form.save(commit=False)
            model_object.pk = pk
            try:
                self.login, self.password = \
                    model_object.save(username=request.user,
                                      groups=account_form.cleaned_data['groups'])
            except Exception as e:
                self.err_msg = e
                customer_form.add_error(None, str(self.err_msg))
        forms = {}
        forms['forms'] = {'customer_form': customer_form,
                          'account_form': account_form}
        return forms

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.set_form_context(**kwargs))

    def post(self, request, *args, **kwargs):
        context = self.get_form_context(request, kwargs.get('pk', kwargs.get('id')))
        if self.err_msg:
            return self.get(context)
        else:
            return redirect(self.success_url)


class ObjectsLists(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    view_title = None
    page_title = None
    permission_required = ''
    heads = None
    create_uri = 'dashboard'
    login_url = reverse_lazy('base_login')

    def get_context_data(self, **kwargs):
        context = super(ObjectsLists, self).get_context_data(**kwargs)
        context['page_title'] = self.view_title
        context['view_title'] = self.view_title
        context['heads'] = self.heads
        context['create_uri'] = self.create_uri
        return context