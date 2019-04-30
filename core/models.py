from django.db import models
from django.contrib.auth.models import User, Permission, Group
from django.core.validators import RegexValidator, EmailValidator


# Расширение модели прав, связка для сервиса
class Service(models.Model):
    fk_permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE)
    description = models.CharField(max_length=50, verbose_name='Наименование')
    url = models.SlugField(unique=True, blank=False, verbose_name='URI ресурса')
    price = models.FloatField(blank=True, verbose_name='Цена')
    status = models.BooleanField(default=True, verbose_name='Статус')
    is_create = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    is_update = models.DateTimeField(auto_now=True, verbose_name='Дата модификации')

    def save(self, *args, **kwargs):
        # Function logging
        log = Protocol()
        log.user = 'Django admin'

        for key in kwargs:
            if key == 'username':
                log.user = kwargs[key]

            if key == 'action':
                action = kwargs[key]

        if self.pk is not None:
            log.action = 'Update service ' + str(self.name) + '. ' + action
        else:
            log.action = 'Insert service ' + str(self.name) + '.'

        try:
            super(Service, self).save(*args, **kwargs)
            #Связь с разрешениями
        except Exception:
            log.action = 'Error for Update Service:' + self.pk
            log.action += 'Exeption:' + str(Exception) + '. Action rollback.'
        finally:
            log.save()

    def not_active(self, **kwargs):
        self.status = False
        self.save(action='Change status SERVICE:' + self.pk + '. Active = False.')

    def active(self, **kwargs):
        self.status = True
        self.save(action='Change status SERVICE:' + self.pk + '. Active = True.')

    def delete(self, user=None, using=None, keep_parents=False):
        log = Protocol()

        if user:
            log.user = user
        else:
            log.user = 'Django admin'

        log.action = 'Delete SERVICE: id = ' + self.pk + ', name: ' + self.name

        try:
            super(Service, self).delete(using=None, keep_parents=False)
        except Exception:
            log = 'Raise exeptions when delete Service:' + self.pk + '. Exeption:' + Exception.__str__ + '.'
        finally:
            log.save()

    def __str__(self):
        return str(self.description)


# пакет услуг подключаемых клиенту. Расширение системы прав.
class Package(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    description = models.CharField(max_length=50, verbose_name='Наименование')
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

    customer = models.ForeignKey(User, on_delete=models.CASCADE)
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

    def create(self, *args, **kwargs):

        super(Customer, self).save(*args, **kwargs)

    def __str__(self):
        return self.description


# Протоколирование действий пользователя.
class Protocol(models.Model):
    action = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action
