from django.db import models
from django.contrib.auth.models import User, Permission
from django.core.validators import RegexValidator, EmailValidator


# Create your models here.
class Services(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=50)
    price = models.FloatField(blank=True)
    fk_permission = models.OneToOneField(Permission, on_delete=models.PROTECT)
    status = models.BooleanField(default=True)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Function logging

        log = CoreProtocol()
        log.user = 'user'
        log.action = 'UPDATE SERVICE:' + str(self.pk)

        try:
            super(Services, self).save(*args, **kwargs)
        except Exception:
            log.action = 'Error for Update Service:' + self.pk
            log.action += 'Exeption:' + str(Exception) + '. Update rollback.'
        finally:
            log.save()

    def not_active(self, user):
        log = CoreProtocol()
        log.user = user
        log.action = 'Change status SERVICE:' + self.pk + '. Active = False'

        self.status = False
        self.save()
        log.save()

    def delete(self, user=None, using=None, keep_parents=False):

        log = CoreProtocol()
        log.user = user
        log.action = 'Delete SERVICE:' + self.pk

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

    def save(self, *args, **kwargs):
        # Function logging

        super(Contract, self).save(*args, **kwargs)


# Данные о юридичском лице
class CustomerInfo(models.Model):
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Телефонный номер должен быть иметь следующий формат: '+999999999'. "
                                         "Максимальное количество цифр 15.")
    d_reg = RegexValidator(regex=r'^\d{9,15}$', message='Введите цифры')
    description = models.CharField(max_length=100)
    OGRN = models.CharField(validators=[d_reg], blank=True, max_length=20)
    INN = models.CharField(validators=[d_reg], blank=True, max_length=20)
    KPP = models.CharField(validators=[d_reg], blank=True, max_length=20)
    legal_address = models.CharField(max_length=250)
    postal_address = models.CharField(max_length=250)
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(validators=[phone_regex], max_length=17)  # validators should be a list
    email_validator = EmailValidator()
    email_address = models.CharField(validators=[email_validator], max_length=15)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Function logging

        super(CustomerInfo, self).save(*args, **kwargs)


# Log
class CoreProtocol(models.Model):
    action = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    action_date = models.DateTimeField(auto_now_add=True)