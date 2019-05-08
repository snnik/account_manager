from django import forms
from django.contrib.auth.models import User, Group

from .models import *


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('description', 'INN', 'KPP', 'legal_address', 'postal_address',
                  'phone_number', 'email_address', )
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'INN': forms.TextInput(attrs={'class': 'form-control'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_address': forms.Textarea(attrs={'class': 'form-control'}),
            'postal_address': forms.Textarea(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'label': 'Логин'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'})
        }


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('description', 'url', 'shortcut_path', 'price', 'status')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'shortcut_path': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ('description', 'status', 'group')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input left'}, ),
            'group': forms.Select(attrs={'class': 'form-control'})
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'permissions')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'permissions': forms.SelectMultiple(attrs={'class': 'form0-control'})
        }
