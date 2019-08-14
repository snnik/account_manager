from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
   # path('account/<int:customer_id>/update/', views.update_account, name='account_update'),
   # Пользователь
   path('account/list/', views.AccountList.as_view(), name='user_list'),
   path('account/create', views.create_user, name='user_create'),
   path('account/<int:user_id>/update', views.update_user, name='user_update'),
   path('account/<int:user_id>/delete', views.delete_user, name='user_delete'),
   # Клиенты
   path('customer/<int:pk>/detail/', views.UpdateCustomer.as_view(), name='account_detail'),
   path('customer/create/', views.CreateCustomer.as_view(), name='account_create'),
   # path('customer_tst/', views.CustomerCreate.as_view()),
   # path('customer/create/', views.create_customer, name='account_create'),
   path('customer/list/', views.CustomerList.as_view(), name='accounts_list'),
   # Группа
   path('group/list/', views.GroupList.as_view(), name='group_list'),
   path('group/create/', views.group_view, name='group_create'),
   path('group/<int:group_id>/detail/', views.group_view, name='group_detail'),
   # Пакеты
   path('package/list', views.PackageList.as_view(), name='package_list'),
   path('package/create', views.PackageCreate.as_view(), name='package_create'),
   path('package/<int:pk>/update/', views.PackageUpdate.as_view(), name='package_update'),
   path('package/<int:pk>/delete/', views.PackageDelete.as_view(), name='package_delete'),
   # Сервисы
   path('service/list/', views.ServiceList.as_view(), name='services_list'),
   path('service/create/', views.ServiceCreate.as_view(), name='service_create'),
   path('service/<int:pk>/update', views.ServiceUpdate.as_view(), name='service_update'),
   path('service/<int:pk>/delete', views.ServiceDelete.as_view(), name='service_delete'),
   # Авторизация
   path('base_login/', views.login, name='base_login'),
   path('logout/', views.logout, name='base_logout'),
   path('pass_change/', views.password_change, name='change_pass'),

   path('profile/', views.profile, name='profile'),
   path('', views.index, name='dashboard'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

