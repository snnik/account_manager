from django.forms import ModelForm
from .models import *


class CustomerForm(ModelForm):
    class Meta:
        model = CustomerInfo
        fields = ('description', 'INN', 'phone_number',)