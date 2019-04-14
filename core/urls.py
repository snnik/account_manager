from django.conf.urls import url, include
from . import views

urlpatterns = [
   url(r'^update/(?P<id>\d+)$', views.update_account),
   url(r'^create$', views.create_account),
   url(r'^delete$', views.delete_account),
   url(r'^$', views.index)
]