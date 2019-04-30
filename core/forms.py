from django import forms
from django.contrib.auth.models import User, Group

from .models import *


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('description', 'INN', 'KPP', 'legal_address', 'postal_address',
                  'phone_number', 'email_address', 'customer',)
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'INN': forms.TextInput(attrs={'class': 'form-control'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_address': forms.Textarea(attrs={'class': 'form-control'}),
            'postal_address': forms.Textarea(attrs={'class': 'form-control'}),
            'customer': forms.widgets.Select(),
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
