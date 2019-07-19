from django.contrib.auth.models import User
from django.views.generic import DetailView, ListView, UpdateView, CreateView, DeleteView, View
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import models
from django import forms
from django.contrib.admin.models import ADDITION, DELETION, CHANGE, LogEntry
from django.shortcuts import render, get_object_or_404, redirect
from core.forms import CreateUserForm, ContentType, CustomerForm, GroupSelectForm
from core.models import Customer


def write_log(usr, obj, flag):
    LogEntry.objects.log_action(
        user_id=usr.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=flag,
        change_message=obj
    )


class ListViewMixin(LoginRequiredMixin, PermissionRequiredMixin, ListView):

    view_title = None
    page_title = None
    permission_required = ''
    heads = None
    create_uri = 'dashboard'
    login_url = reverse_lazy('base_login')

    def get_context_data(self, **kwargs):
        context = super(ListViewMixin, self).get_context_data(**kwargs)
        context['page_title'] = self.view_title
        context['view_title'] = self.view_title
        context['heads'] = self.heads
        context['create_uri'] = self.create_uri
        return context


class CreateFormMixin(CreateView, LoginRequiredMixin, PermissionRequiredMixin):

    form_title = None
    page_title = None
    permission_required = ''
    login_url = reverse_lazy('base_login')
    prev_uri = 'dashboard'

    def get_context_data(self, **kwargs):
        if 'form_title' not in kwargs:
            kwargs['form_title'] = self.form_title

        if 'page_title' not in kwargs:
            kwargs['page_title'] = self.page_title

        if 'prev_uri' not in kwargs:
            kwargs['prev_uri'] = self.prev_uri

        return super().get_context_data(**kwargs)


class UpdateFormMixin(UpdateView, LoginRequiredMixin, PermissionRequiredMixin):

    form_title = None
    page_title = None
    permission_required = ''
    login_url = reverse_lazy('base_login')
    success_url = reverse_lazy('base_login')
    prev_uri = 'dashboard'

    def get_context_data(self, **kwargs):
        if 'form_title' not in kwargs:
            kwargs['form_title'] = self.form_title

        if 'page_title' not in kwargs:
            kwargs['page_title'] = self.page_title

        if 'prev_uri' not in kwargs:
            kwargs['prev_uri'] = self.prev_uri

        return super().get_context_data(**kwargs)