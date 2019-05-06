from django.urls import path
from . import views

urlpatterns = [
   path('account/<int:customer_id>/update/', views.update_account, name='account_update'),
   path('account/<int:customer_id>/detail/', views.account_detail, name='account_detail'),
   path('account/create/', views.create_account, name='account_create'),
   path('account/<int:customer_id>/deactivate/', views.deactivate_account, name='account_deactivate'),
   path('account/<int:customer_id>/activate/', views.activate_account, name='account_activate'),
   path('accounts/list/', views.accounts_list, name='accounts_list'),
   path('service/list/', views.services_list, name='services_list'),
   path('service/create/', views.create_service, name='service_create'),
   path('service/<int:service_id>/update', views.update_service),
   path('service/<int:service_id>/delete', views.delete_service),
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('passchange/', views.password_change, name='passchange'),
   path('', views.index, name='dashboard')
]