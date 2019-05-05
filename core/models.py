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
        for key in kwargs:
            if key == 'username':
                log.user = kwargs[key]

            if key == 'action':
                action = kwargs[key]

        if self.pk is not None:
            log.action = 'Изменение сервиса: ' + str(self.name) + '. ' + action
        else:
            log.action = 'Добавление сервиса ' + str(self.name) + '.'

        try:
            super(Service, self).save(*args, **kwargs)
            #Связь с разрешениями
        except Exception:
            log.action = 'Ошибка при изменении сервиса:' + self.pk
            log.action += 'Exception:' + str(Exception) + '. Action rollback.'
        finally:
            log.save()

    def not_active(self, **kwargs):
        self.status = False
        self.save(action='Отключение сервиса:' + self.pk + '. Active = False.')

    def active(self, **kwargs):
        self.status = True
        self.save(action='Вкючение сервиса:' + self.pk + '. Active = True.')

    def delete(self, user=None, using=None, keep_parents=False):
        log = Protocol()
        if user:
            log.user = user
        log.action = 'Удаление сервиса: id = ' + self.pk + ', name: ' + self.name
        try:
            super(Service, self).delete(using=None, keep_parents=False)
        except Exception:
            log = 'Ошибка при удалении сервиса:' + self.pk + '. Exception:' + Exception.__str__ + '.'
        finally:
            log.save()

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
        if not self.pk:
            login = LoginGenerator().create_login(self.description)
            password = PasswordGenerator().generate()
            try:
                user = User.objects.create_user(username=login, password=password)
            except Exception:
                login = ''
                postfix = str(time.time()).split('.')[1]
                login = LoginGenerator().create_login(self.description, postfix)
                user = User.objects.create_user(username=login, password=password)

        self.customer = user
        super(Customer, self).save(*args, **kwargs)

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

    def __str__(self):
        return self.action
