from django.urls import path
from . import views

urlpatterns = [
   path('update/<int:id>/', views.update_account),
   path('create/', views.create_account),
   path('delete/', views.delete_account),
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('', views.index)
]