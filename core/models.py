from django.db import models
from django.contrib.auth.models import User, Permission
from django.core.validators import RegexValidator, EmailValidator


class Services(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=50)
    url = models.SlugField(unique=True, blank=False)
    price = models.FloatField(blank=True)
    fk_permission = models.OneToOneField(Permission, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Function logging
        log = CoreProtocol()
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
            super(Services, self).save(*args, **kwargs)
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
        log = CoreProtocol()

        if user:
            log.user = user
        else:
            log.user = 'Django admin'

        log.action = 'Delete SERVICE: id = ' + self.pk + ', name: ' + self.name

        try:
            super(Services, self).delete(using=None, keep_parents=False)
        except Exception:
            log = 'Raise exeptions when delete Service:' + self.pk + '. Exeption:' + Exception.__str__() + '.'
        finally:
            log.save()

    def __str__(self):
        return str(self.description)


#Contract
class Contract(models.Model):
    number = models.CharField(max_length=10, unique=True)
    customer = models.ManyToManyField(User)
    status = models.BooleanField(default=True)
    services = models.ManyToManyField(Services)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.number + ' ' + str(self.customer.name)


# Данные о юридичском лице
class CustomerInfo(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Телефонный номер должен быть иметь следующий формат: '+999999999'. "
                                         "Максимальное количество цифр 15.")
    d_reg = RegexValidator(regex=r'^\d{9,15}$', message='Введите цифры')
    email_validator = EmailValidator()

    description = models.CharField(max_length=100)
    OGRN = models.CharField(validators=[d_reg], blank=True, max_length=20)
    INN = models.CharField(validators=[d_reg], blank=True, max_length=20)
    KPP = models.CharField(validators=[d_reg], blank=True, max_length=20)
    legal_address = models.CharField(max_length=250)
    postal_address = models.CharField(max_length=250)
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)  # validators should be a list
    email_address = models.CharField(validators=[email_validator], max_length=15)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.description


# Log
class CoreProtocol(models.Model):
    action = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    action_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.action