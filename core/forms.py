from django import forms
from django.db import Error
from .models import Customer, Service, Package
from django.contrib.auth import password_validation
from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.admin.models import ADDITION, LogEntry, DELETION, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail


class CustomerForm(forms.ModelForm):
    user = None
    groups = None
    form_error = []

    class Meta:
        model = Customer
        fields = ('name', 'INN', 'KPP', 'OGRN', 'legal_address', 'postal_address',
                  'phone_number', 'email_address',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'INN': forms.TextInput(attrs={'class': 'form-control'}),
            'KPP': forms.TextInput(attrs={'class': 'form-control'}),
            'OGRN': forms.TextInput(attrs={'class': 'form-control'}),
            'legal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email_address': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def changed_groups(self, o):
        o.groups.clear()
        try:
            for group in self.groups:
                o.groups.add(group)
            LogEntry.objects.log_action(
                user_id=self.user.pk,
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=o.pk,
                object_repr=repr(o),
                action_flag=CHANGE,
                change_message=o
            )
        except Error as e:
            self.form_error.append(str(e))

    def create_customer(self):
        instance = super(Customer, self).save(commit=False)
        try:
            account = instance.create_user()
            LogEntry.objects.log_action(
                user_id=self.user.pk,
                content_type_id=ContentType.objects.get_for_model(User).pk,
                object_id=account.pk,
                object_repr=repr(account),
                action_flag=ADDITION,
                change_message=account
            )
        except Error as e:
            self.form_error.append(str(e))
        send_mail('Пароль',
                  'Учетные данные:' +
                  str(instance.account_login) +
                  ' ' +
                  str(instance.password),
                  'snnik1@gmail.com',
                  'snnik@live.com'
                  )
        self.changed_groups(account)
        try:
            instance.save()
            LogEntry.objects.log_action(
                user_id=self.user.pk,
                content_type_id=ContentType.objects.get_for_model(Customer).pk,
                object_id=instance.pk,
                object_repr=repr(instance),
                action_flag=ADDITION,
                change_message=instance
            )
        except Error as e:
            self.form_error.append(str(e))
        if instance.model_error:
            self.form_error.append(instance.model_error)
        return instance.pk

    def update_customer(self):
        instance = super(Customer, self).save(commit=False)
        self.changed_groups(instance.account)
        try:
            instance.save()
            LogEntry.objects.log_action(
                user_id=self.user.pk,
                content_type_id=ContentType.objects.get_for_model(Customer).pk,
                object_id=instance.pk,
                object_repr=repr(instance),
                action_flag=CHANGE,
                change_message=instance
            )
        except Error as e:
            self.form_error.append(str(e))
        return instance.pk

    def delete_customer(self):
        instance = super(Customer, self).save(commit=False)
        try:
            instance.delete_entity()
            LogEntry.objects.log_action(
                user_id=self.user.pk,
                content_type_id=ContentType.objects.get_for_model(Customer).pk,
                object_id=instance.pk,
                object_repr=repr(instance),
                action_flag=CHANGE,
                change_message=instance)
        except Error as e:
            self.form_error.append(str(e))


class GroupSelectForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('groups',)
        widgets = {
            'groups': forms.CheckboxSelectMultiple()
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
    user = None
    form_error = []

    class Meta:
        model = Service
        fields = ('name', 'url_path', 'shortcut_path', 'price', 'status', 'is_service')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'url_path': forms.TextInput(attrs={'class': 'form-control'}),
            'shortcut_path': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.CheckboxInput(),
            'is_service': forms.CheckboxInput(),
        }


class PackageForm(forms.ModelForm):
    description = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Package
        fields = ('status', 'price')
        widgets = {
            'status': forms.CheckboxInput(),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ('name', 'permissions',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'permissions': forms.CheckboxSelectMultiple()
        }


class ChangePasswordForm(PasswordChangeForm):
    def save(self, user):
        user.set_password(self.cleaned_data['password'])
        user.save()
        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(User).pk,
            object_id=user.pk,
            object_repr=repr(self),
            action_flag=CHANGE)


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


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', )
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

