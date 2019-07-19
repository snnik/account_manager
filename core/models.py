import time
from django.db import models, Error
from django.contrib.auth.models import User, Permission, Group
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.contenttypes.models import ContentType
from .utils import PasswordGenerator, LoginGenerator
from django.contrib.admin.models import ADDITION, LogEntry, DELETION, CHANGE


def write_log(usr, obj, flag):
    LogEntry.objects.log_action(
        user_id=usr.pk,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=repr(obj),
        action_flag=flag,
        change_message=obj
    )


# Данные о юридичском лице. Расширение стандартного пользователя
class Customer(models.Model):
    account_login = None
    account_password = None
    model_error = None
    user = None
    groups = None

    phone_regex = RegexValidator(regex=r'^\+?1?\d{6,15}$',
                                 message="Телефонный номер должен быть иметь следующий формат: '+999999999'. "
                                         "Максимальное количество цифр 15.")
    d_reg = RegexValidator(regex=r'^\d{9,15}$', message='Введите цифры')
    email_validator = EmailValidator()

    account = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=100, verbose_name='Наименование')
    OGRN = models.CharField(validators=[d_reg], blank=True, max_length=20, verbose_name='ОГРН')
    INN = models.CharField(validators=[d_reg], blank=True, max_length=20, verbose_name='ИНН')
    KPP = models.CharField(validators=[d_reg], blank=True, max_length=20, verbose_name='КПП')
    legal_address = models.CharField(max_length=250, blank=True, verbose_name='Адрес фактический')
    postal_address = models.CharField(max_length=250, blank=True, verbose_name='Адрес юридический')
    phone_number = models.CharField(validators=[phone_regex], max_length=17, verbose_name='Номер телефона')
    email_address = models.CharField(validators=[email_validator], max_length=15, verbose_name='Электронная почта')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def __str__(self):
        return self.name

    def create_user(self):
        self.account_login = LoginGenerator().create(self.name)
        self.account_password = PasswordGenerator().generate()
        try:
            account = User.objects.create_user(username=self.account_login,
                                               password=self.account_password)
        except Error as e:
            postfix = str(time.time()).split('.')[1]
            self.account_login = LoginGenerator().create(self.name, postfix)
            account = User.objects.create_user(username=self.account_login,
                                               password=self.account_password)
            self.model_error = str(e)
        write_log(self.user, account, ADDITION)
        return account

    def save(self, *args, **kwargs):
        if self.pk:
            account = self.account
            # account.groups.clear()
            flag = CHANGE
        else:
            account = self.create_user()
            self.account = account
            flag = ADDITION
        # groups = list(self.groups)
        account.groups.set(self.groups)
        write_log(self.user, account, CHANGE)
        try:
            super(Customer, self).save(*args, **kwargs)
            write_log(self.user, self, flag)
        except Error as e:
            pass

    def delete_entity(self):
        account = self.account
        account.is_active = False
        account.save()


# Расширение модели прав, связка для сервиса
class Service(models.Model):
    model_error = None
    fk_permission = models.OneToOneField(
        Permission,
        on_delete=models.CASCADE, blank=True)
    name = models.CharField(max_length=50, verbose_name='Наименование')
    url_path = models.TextField(unique=True, blank=False, verbose_name='URI ресурса')  # !!!!
    shortcut_path = models.ImageField(verbose_name='Путь к ярлыку')
    is_service = models.BooleanField(default=True, verbose_name='Служебный')
    status = models.BooleanField(default=True, verbose_name='Статус')
    price = models.FloatField(blank=True, verbose_name='Цена')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def permission_name_generator(self):
        t = LoginGenerator()
        return str(self.pk) + '_service_' + str(t.translit(self.name))

    def permission_create(self):
        permission, flag = Permission.objects.get_or_create(
            codename=self.permission_name_generator(),
            name=self.name,
            content_type=ContentType.objects.get_for_model(Service),
        )
        self.fk_permission = permission

    def set_service_price(self):
        if self.is_service:
            self.price = 0

    def delete(self, *args, **kwargs):
        pass

    def __str__(self):
        return str(self.name)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('service_update', kwargs={'pk': str(self.pk)})


# пакет услуг подключаемых клиенту. Расширение системы групп.
class Package(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, blank=True)
    price = models.FloatField(blank=True, verbose_name='Цена')
    status = models.BooleanField(default=True, verbose_name='Активен')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def set_group_fk(self, group_name=None):
        if group_name:
            group, flag = Group.objects.get_or_create(name=group_name)
            self.group = group

    def set_permissions(self, permissions=None):
        if permissions:
            # self.group.permissions.clear()
            self.group.permissions.set(list(permissions))

    def delete(self, using=None, keep_parents=False):
        self.status = False
        return super(Package, self).save()

    def __str__(self):
        return self.group.name
