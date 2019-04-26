from django import forms
from .models import *


class CustomerForm(forms.ModelForm):
    class Meta:
        model = CustomerInfo
        fields = ('description', 'INN', 'KPP', 'legal_address', 'postal_address',
                  'phone_number', 'email_address', 'customer')
        widgets = {
            'description': forms.TextInput(attrs={'class':'form-control'}),
            'INN': forms.TextInput(attrs={'class':'form-control'}),
            'KPP': forms.TextInput(attrs={'class':'form-control'}),
            'legal_address': forms.Textarea(attrs={'class':'form-control'}),
            'postal_address': forms.Textarea(attrs={'class':'form-control'}),
            'customer': forms.widgets.Select(),
            'phone_number': forms.TextInput(attrs={'class':'form-control'}),
            'email_address': forms.TextInput(attrs={'class':'form-control'}),
        }