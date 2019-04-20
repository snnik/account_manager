from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator, EmailValidator


# Create your models here.
class Services(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.CharField(max_length=50)
    status = models.BooleanField(default=True)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Function logging

        super(Services, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.status = False
        self.save()


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
class customer_info(models.Model):
    description = models.CharField(max_length=100)
    OGRN = models.IntegerField(blank=True)
    INN = models.IntegerField(blank=True)
    KPP = models.IntegerField(blank=True)
    legal_address = models.CharField(max_length=250)
    postal_address = models.CharField(max_length=250)
    customer = models.OneToOneField(User, on_delete='CASCADE')
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Телефонный номер должен быть иметь следующий формат: '+999999999'. "
                                         "Максимальное количество цифр 15.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17)  # validators should be a list
    email_validator = EmailValidator()
    email_address = models.CharField(validators=[email_validator], max_length=15)
    is_create = models.DateTimeField(auto_now_add=True)
    is_update = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Function logging

        super(customer_info, self).save(*args, **kwargs)


# Log
class core_protocol(models.Model):
    action = models.CharField(max_length=200)
    user = models.CharField(max_length=200)
    action_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Function logging

        super(core_protocol, self).save(*args, **kwargs)
