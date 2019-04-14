from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Services(models.Model):
    name = models.CharField(max_length = 20)
    description = models.CharField(max_length = 50)
    status = models.BooleanField()

class Contract(models.Model):
    number = models.CharField(max_length = 10)
    customer = models.ManyToManyField(User)
services = models.ManyToManyField(Services)
