from django.urls import path
from . import views

urlpatterns = [
   # path('account/<int:customer_id>/update/', views.update_account, name='account_update'),
   # Пользователь
   path('account/list/', views.AccountList.as_view(), name='user_list'),
   path('account/create', views.create_user, name='user_create'),
   path('account/<int:user_id>/update', views.update_user, name='user_update'),
   path('account/<int:user_id>/delete', views.delete_user, name='user_delete'),
   # Клиенты
   path('customer/<int:customer_id>/detail/', views.account_detail, name='account_detail'),
   path('customer/create/', views.create_account, name='account_create'),
   path('customer/<int:customer_id>/deactivate/', views.deactivate_account, name='account_deactivate'),
   path('customer/<int:customer_id>/activate/', views.activate_account, name='account_activate'),
   path('customer/list/', views.CustomerList.as_view(), name='accounts_list'),
   # Группа
   path('group/list/', views.GroupList.as_view(), name='group_list'),
   # Пакеты
   path('package/list', views.PackageList.as_view(), name='package_list'),
   path('package/create', views.create_package, name='package_create'),
   path('package/<int:sp_id>/update/', views.update_package, name='package_update'),
   path('package/<int:sp_id>/delete/', views.delete_package, name='package_delete'),
   # Сервисы
   path('service/list/', views.ServiceList.as_view(), name='services_list'),
   path('service/create/', views.create_service, name='service_create'),
   path('service/<int:service_id>/update', views.update_service, name='service_update'),
   path('service/<int:service_id>/delete', views.delete_service, name='service_delete'),
   # Авторизация
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('pass_change/', views.password_change, name='change_pass'),
   path('', views.index, name='dashboard')
]
