from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
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


class ChangePassword(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'required': True}),
        label='Пароль',
        help_text='<p>Ваш пароль не должен совпадать с вашим именем или ' +
                  'другой персональной информацией или быть слишком' +
                  'похожим на неё.</p> <ul><li>Ваш пароль должен содержать как минимум ' +
                  '8 символов.</li><li>Ваш пароль не может быть одним из широко' +
                  'распространённых паролей.</li><li>Ваш пароль не может состоять' +
                  'только из цифр.</li></ul>'
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password_confirm', 'required': True}),
        label='Подтверждение пароля')

    def clean(self):
        cleaned_data = super(ChangePassword, self).clean()
        if not cleaned_data['password'] == cleaned_data['password_confirm']:
            raise forms.ValidationError('Пароли не совпадают. Повторите ввод паролей.')

    def save(self, user):
            user.set_password(self.cleaned_data['password'])
            user.save()


class AccountChangeForm(UserChangeForm):
    def add_group(self, instance, groups):
        try:
            if groups:
                instance.groups.clear()
                for g in groups:
                    instance.groups.add(g)
        except Exception as e:
            self.add_error(None, str(e))

    def save(self, commit=True, *args, **kwargs):
        instance = super(AccountChangeForm, self).save(commit=False)
        if commit:
            try:
                instance.save()
            except Exception as e:
                self.add_error(None, str(e))
            self.add_group(instance, self.cleaned_data['groups'])
            LogEntry.objects.log_action(
                user_id=kwargs.get('user_id'),
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=instance.pk,
                object_repr=repr(instance),
                action_flag=CHANGE)
            return instance
        else:
            return instance


class AccountCreationForm(UserCreationForm):
    def account_create(self, *args, **kwargs):
        if self.cleaned_data['password1'] == self.cleaned_data['password2']:
            try:
                account = User.objects.create_user(
                    username=self.cleaned_data['username'],
                    password=self.cleaned_data['password1']
                )
                LogEntry.objects.log_action(
                    user_id=kwargs.get('user_id'),
                    content_type_id=ContentType.objects.get_for_model(User).pk,
                    object_id=account.pk,
                    object_repr=repr(account),
                    action_flag=ADDITION
                )
            except Exception as e:
                self.add_error(None, str(e))
                account = None
        else:
            self.add_error('password1', 'Пароли не совпадают')
        return account


class GroupCreateForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'permissions')

    def add_permissions(self, instance):
        permissions = self.cleaned_data['permissions']
        instance.permissions.clear()
        try:
            for p in permissions:
                instance.permissions.add(p)
        except Exception as e:
            self.add_error(str(e))

    def save(self, commit=True, *args, **kwargs):
        instance = super(GroupCreateForm, self).save(commit=False)
        if instance.pk:
            flag = CHANGE
        else:
            flag = ADDITION
        if commit:
            try:
                instance.save()
                self.add_permissions(instance)
            except Exception as e:
                self.add_error(None, str(e))
            LogEntry.objects.log_action(
                user_id=kwargs.get('user_id'),
                content_type_id=ContentType.objects.get_for_model(Group).pk,
                object_id=instance.pk,
                object_repr=repr(instance),
                action_flag=flag)
            return instance
        else:
            return instance