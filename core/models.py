import time
from django.db import models, Error
from django.contrib.auth.models import User, Permission, Group
from django.core.validators import RegexValidator, EmailValidator
from .utils import PasswordGenerator, LoginGenerator


# Расширение модели прав, связка для сервиса
class Service(models.Model):
    fk_permission = models.OneToOneField(
        Permission,
        on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=50, verbose_name='Наименование')
    status = models.BooleanField(default=True, verbose_name='Статус')
    price = models.FloatField(blank=True, verbose_name='Цена')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def save(self, *args, **kwargs):
        # Function logging
        log = Protocol()
        table = 'core_service'
        if self.pk is not None:
            action = 'change'
        else:
            action = 'add'
        try:
            super(Service, self).save(*args, **kwargs)
            log.save(user=kwargs['username'], action=action, obj=str(self), obj_id=self.pk, table=table)
            #Связь с разрешениями
        except Exception:
            log.save(user=kwargs['username'], action=action, obj=str(self), obj_id=self.pk, table=table, error=str(Exception))

    def not_active(self, **kwargs):
        self.status = False
        self.save(username=kwargs['username'])

    def active(self, **kwargs):
        self.status = True
        self.save(username=kwargs['username'])

    def delete(self, *args, **kwargs):
        log = Protocol()
        action = 'delete'
        table = 'core_service'
        try:
            super(Service, self).delete(using=None, keep_parents=False)
            log.save(user=kwargs['username'], action=action, obj=str(self), obj_id=self.pk, table=table)
        except Exception:
            log.save(user=kwargs['username'], action=action, obj=str(self), obj_id=self.pk, table=table, error=str(Exception))

    def __str__(self):
        return str(self.description)


# пакет услуг подключаемых клиенту. Расширение системы прав.
class Package(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE, blank=True)
    description = models.CharField(max_length=50, verbose_name='Наименование')
    url = models.SlugField(unique=True, blank=False, verbose_name='URI ресурса')
    shortcut_path = models.TextField(verbose_name='Путь к ярлыку')
    price = models.FloatField(blank=True, verbose_name='Цена')
    status = models.BooleanField(default=True, verbose_name='Активен')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def __str__(self):
        return self.description


# Данные о юридичском лице. Расширение стандартного пользователя
class Customer(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
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

    def save(self, *args, **kwargs):
        for key in kwargs:
            if key == 'username':
                usr = kwargs[key]
            else:
                usr = None

            if key == 'password':
                password = kwargs[key]
            else:
                password = None

        if not self.pk:
            action = 'add'
            log = Protocol()
            table = 'auth_user'
            login = LoginGenerator().create_login(self.description)
            password = PasswordGenerator().generate()
            try:
                user = User.objects.create_user(username=login, password=password)
                log.save(action=action, obj=str(user.username), table=table, user=usr, obj_id=user.pk)

            except Exception:
                login = ''
                postfix = str(time.time()).split('.')[1]
                login = LoginGenerator().create_login(self.description, postfix)
                user = User.objects.create_user(username=login, password=password)
                log.save(action=action, obj=str(user.username), table=table, user=usr, obj_id=user.pk)
            table = 'core_customer'
            self.customer = user
        else:
            action = 'change'
            table = 'core_customer'

        clog = Protocol()
        try:
            super(Customer, self).save(*args, **kwargs)
            clog.save(action=action, obj=str(self), table=table, user=usr, obj_id=self.pk)
        except Exception:
            clog.save(clog.save(action=action, obj=str(self), table=table, user=usr,
                                obj_id=self.pk), error=str(Exception))
        return password

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

        if 'user' in kwargs:
            self.user = kwargs['user']
            del(kwargs['user'])
        elif 'obj' in kwargs:
            obj = str(kwargs['obj'])
            del(kwargs['obj'])
        elif 'table' in kwargs:
            table = str(kwargs['table'])
            del(kwargs['table'])
        elif 'obj_id' in kwargs:
            obj_id = str(kwargs['obj_id'])
            del(kwargs['obj_id'])

        if error:
            self.action = 'Ошибка: ' + error + 'При попытке внести изменения в таблицу ' + table + \
                          ' пользователем ' + self.user + './n' + \
                          'Объект:' + obj + '. ID записи:' + obj_id + '. Действие: ' + action

        if action == 'delete':
            self.action = 'Удален ' + obj + ' пользователем ' + self.user + './n' \
                          + 'Таблица:' + table + '. ID записи:' + obj_id
        elif action == 'change':
            self.action = 'Изменен ' + obj + ' пользователем ' + str(self.user) + './n' \
                      + 'Таблица:' + table + '. ID записи:' + obj_id
        elif action == 'add':
            self.action = 'Добавлен ' + obj + ' пользователем ' + self.user + './n' \
                          + 'Таблица ' + table + '. ID записи: ' + obj_id
        else:
            self.action = 'Действие не определено. Пользователь:' + self.user + ', объект: ' + object + '.'

        kwargs = {}

        super(Protocol, self).save(*args, **kwargs)

    def __str__(self):
        return self.action
