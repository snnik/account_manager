from django import forms
from .models import *
from django.contrib.auth import password_validation


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ('description', 'INN', 'KPP', 'OGRN', 'legal_address', 'postal_address',
                  'phone_number', 'email_address', )
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'INN': forms.TextInput(attrs={'class': 'form-control'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control'}),
            'OGRN': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('groups', )
        widgets = {
            'groups': forms.CheckboxSelectMultiple(),
        }


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'groups', 'is_staff', 'is_superuser', 'is_active')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'label': 'Логин'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.TextInput(attrs={'class': 'form-control'}),
            'groups': forms.CheckboxSelectMultiple(),
            'is_staff': forms.CheckboxInput(),
            'is_superuser': forms.CheckboxInput(),
            'is_active': forms.CheckboxInput(),
        }


class CreateUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

    # password = forms.CharField(
    #     widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    #     help_text='Ваш пароль не должен совпадать с вашим именем или' +
    #               'другой персональной информацией или быть слишком' +
    #               'похожим на неё.\n Ваш пароль должен содержать как минимум' +
    #               '8 символов.\n Ваш пароль не может быть одним из широко' +
    #               'распространённых паролей.\n Ваш пароль не может состоять' +
    #               'только из цифр.',
    #     label='Пароль:',
    #     validators=password_validation.get_default_password_validators()
    # )

    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}),
        label='Подтверждение пароля',
        help_text='Подтвердите пароль',
        )

    # Перегрузить метод save
    def clean(self):
        cleaned_data = super(CreateUserForm, self).clean()
        password_validation.validate_password(cleaned_data['password'])
        if not cleaned_data['password1'] == cleaned_data['password']:
            raise forms.ValidationError('Пароли не совпадают. Повторите ввод паролей.')


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ('description', 'url', 'shortcut_path', 'price', 'status', 'is_service')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'url': forms.TextInput(attrs={'class': 'form-control'}),
            'shortcut_path': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(),
            'is_service': forms.CheckboxInput(),
        }


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ('description', 'status', 'price')
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GroupForm(forms.ModelForm):

    class Meta:
        model = Group
        fields = ('permissions',)
        widgets = {
            'permissions': forms.CheckboxSelectMultiple()
        }
