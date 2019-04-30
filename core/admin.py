from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Service)
admin.site.register(Package)
admin.site.register(CustomerInfo)
admin.site.register(CoreProtocol)