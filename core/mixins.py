from django.views.generic import ListView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse_lazy


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


class DeleteFormMixin(DeleteView, LoginRequiredMixin, PermissionRequiredMixin):

    login_url = reverse_lazy('base_login')
    success_url = reverse_lazy('dashboard')
    prev_uri = 'dashboard'
    form_title = None
    page_title = None
    permission_required = ''

    def get_context_data(self, **kwargs):
        if 'form_title' not in kwargs:
            kwargs['form_title'] = self.form_title

        if 'page_title' not in kwargs:
            kwargs['page_title'] = self.page_title

        if 'prev_uri' not in kwargs:
            kwargs['prev_uri'] = self.prev_uri

        return super().get_context_data(**kwargs)


