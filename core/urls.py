from django.urls import path
from . import views

urlpatterns = [
   path('account/<int:id>/update/', views.update_account, name='account_update'),
   path('account/<int:id>/detail/', views.account_detail, name='account_detail'),
   path('account/create/', views.create_account, name='account_create'),
   path('account/<int:id>/delete/', views.delete_account, name='account_delete'),
   path('accounts/list/', views.accounts_list, name='accounts_list'),
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('', views.index, name='dashboard')
]