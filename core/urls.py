from django.urls import path
from . import views

urlpatterns = [
   path('account/<int:id>/update/', views.update_account),
   path('account/create/', views.create_account),
   path('account/<int:id>/delete/', views.delete_account),
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('', views.index)
]