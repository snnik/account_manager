import time
from django.db import models, Error
from django.contrib.auth.models import User, Permission, Group
from django.core.validators import RegexValidator, EmailValidator
from django.contrib.contenttypes.models import ContentType
from .utils import PasswordGenerator, LoginGenerator
from django.contrib.admin.models import ADDITION, LogEntry, DELETION, CHANGE
from django.core.mail import send_mail


# Расширение модели прав, связка для сервиса
class Service(models.Model):
    fk_permission = models.OneToOneField(
        Permission,
        on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=50, verbose_name='Наименование')
    url = models.TextField(unique=True, blank=False, verbose_name='URI ресурса')  # !!!!
    shortcut_path = models.TextField(verbose_name='Путь к ярлыку')
    is_service = models.BooleanField(default=True, verbose_name='Услуга/Служебный')
    status = models.BooleanField(default=True, verbose_name='Статус')
    price = models.FloatField(blank=True, verbose_name='Цена')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def save(self, *args, **kwargs):
        user = kwargs.get('username')
        if not self.is_service:
            self.price = 0
        try:
            if self.pk:
                action = CHANGE
            else:
                action = ADDITION
                translit_str = LoginGenerator()
                content_type = ContentType.objects.get_for_model(Service)
                permission, flag = Permission.objects.get_or_create(
                    codename=translit_str.translit(self.description),
                    name=self.description,
                    content_type=content_type,
                )
                self.fk_permission = permission
            kwargs.clear()
            super(Service, self).save(*args, **kwargs)
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=content_type.pk,
                object_id=self.pk,
                object_repr=repr(self),
                action_flag=action,
                change_message=self
            )
        except Exception as e:
            print(str(e))

    def not_active(self, **kwargs):
        self.status = False
        self.save(username=kwargs.get('username'))

    def active(self, **kwargs):
        self.status = True
        self.save(username=kwargs.get('username'))

    def delete(self, *args, **kwargs):
        user = kwargs.get('username')
        try:
            super(Service, self).delete(using=None, keep_parents=False)
            LogEntry.objects.log_action(
                user_id=user.id,
                content_type_id=ContentType.objects.get_for_model(Service).pk,
                object_id=self.pk,
                object_repr=repr(self),
                action_flag=DELETION,
                change_message=self
            )
        except Exception as e:
            print(str(e))

    def __str__(self):
        return str(self.description)


# пакет услуг подключаемых клиенту. Расширение системы групп.
class Package(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=50, verbose_name='Наименование')
    price = models.FloatField(blank=True, verbose_name='Цена')
    status = models.BooleanField(default=True, verbose_name='Активен')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def save(self, *args, **kwargs):
        tg = LoginGenerator()
        user = kwargs.get('username')
        permissions = kwargs.get('permissions')
        group_name = kwargs.get('group', tg.translit(self.description))
        try:
            group, flag = Group.objects.get_or_create(name=group_name)
            if flag:
                action = ADDITION
            else:
                action = CHANGE
                group.permissions.clear()
        except Exception as e:
            print(str(e))
        if permissions:
            for permission in permissions:
                group.permissions.add(permission)
        LogEntry.objects.log_action(
            user_id=user.id,
            content_type_id=ContentType.objects.get_for_model(Service).pk,
            object_id=self.pk,
            object_repr=repr(self),
            action_flag=action,
            change_message=self
        )
        try:
            if self.pk:
                action = CHANGE
            else:
                action = ADDITION
            self.group = group
            kwargs.clear()
            super(Package, self).save(*args, **kwargs)
        except Exception as e:
            print(str(e))

    def __str__(self):
        return self.description


# Данные о юридичском лице. Расширение стандартного пользователя
class Customer(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{6,15}$',
                                 message="Телефонный номер должен быть иметь следующий формат: '+999999999'. "
                                         "Максимальное количество цифр 15.")
    d_reg = RegexValidator(regex=r'^\d{9,15}$', message='Введите цифры')
    email_validator = EmailValidator()

    customer = models.OneToOneField(User, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=100, verbose_name='Наименование')
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
        return self.description

    def create_user(self, **kwargs):
        login = None
        password = None
        user = kwargs.get('username')
        password = kwargs.get('password')
        login = LoginGenerator().create(self.description)
        password = PasswordGenerator().generate()
        try:
            account = User.objects.create_user(username=login, password=password)
        except Exception as e:
            postfix = str(time.time()).split('.')[1]
            login = LoginGenerator().create(self.description, postfix)
            account = User.objects.create_user(username=login, password=password)
        send_mail('Пароль',
                  'Учетные данные' + str(login) + ' ' + str(password),
                  'snnik1@gmail.com',
                  [self.email_address]
                  )
        LogEntry.objects.log_action(
            user_id=user.pk,
            content_type_id=ContentType.objects.get_for_model(User).pk,
            object_id=account.pk,
            object_repr=repr(account),
            action_flag=ADDITION,
            change_message=account
        )
        return account

    def save(self, *args, **kwargs):
        groups = kwargs.get('groups')
        user = kwargs.get('username')
        if not self.pk:
            flag = ADDITION
            account = self.create_user(**kwargs)
            self.customer = account
        else:
            flag = CHANGE
            account = self.customer
            account.groups.clear()
        for group in groups:
            account.groups.add(group)
        kwargs.clear()
        try:
            super(Customer, self).save(*args, **kwargs)
            LogEntry.objects.log_action(
                user_id=user.pk,
                content_type_id=ContentType.objects.get_for_model(Customer).pk,
                object_id=self.pk,
                object_repr=repr(self),
                action_flag=flag,
                change_message=self
            )
        except Exception as e:
            print(str(e))

    def activate(self):
        user = self.customer
        user.is_active = True
        user.save()

    def deactivate(self):
        user = self.customer
        user.is_active = False
        user.save()


# Протоколирование действий пользователя.
class Protocol(models.Model):
    action = models.CharField(max_length=200)
    user = models.CharField(max_length=200, default='Django admin')
    action_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        error = kwargs.get('error')
        action = kwargs.get('action')
        self.user = str(kwargs.get('user'))
        obj = str(kwargs.get('obj'))
        table = str(kwargs.get('table'))
        obj_id = str(kwargs.get('obj_id'))

        if error:
            self.action = 'Ошибка: ' + error + 'При попытке внести изменения в таблицу ' + table + \
                          ' пользователем ' + self.user + '.\n' + \
                          'Объект:' + obj + '. ID записи:' + obj_id + '. Действие: ' + action

        if action == 'delete':
            self.action = 'Удален ' + obj + ' пользователем ' + self.user + '.\n' \
                          + 'Таблица:' + table + '. ID записи:' + obj_id
        elif action == 'change':
            self.action = 'Изменен ' + obj + ' пользователем ' + self.user + '.\n' \
                      + 'Таблица:' + table + '. ID записи:' + obj_id
        elif action == 'add':
            self.action = 'Добавлен ' + obj + ' пользователем ' + self.user + '.\n' \
                          + 'Таблица ' + table + '. ID записи: ' + obj_id
        else:
            self.action = 'Действие не определено. Пользователь:' + self.user + ', объект: ' + obj + '.'

        kwargs.clear()

        super(Protocol, self).save(*args, **kwargs)

    def __str__(self):
        return self.action
