# Generated by Django 2.2 on 2019-04-30 06:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0011_update_proxy_permissions'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoreProtocol',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=200)),
                ('user', models.CharField(max_length=200)),
                ('action_date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='CustomerInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=100, verbose_name='Наименование')),
                ('OGRN', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(message='Введите цифры', regex='^\\d{9,15}$')], verbose_name='ОГРН')),
                ('INN', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(message='Введите цифры', regex='^\\d{9,15}$')], verbose_name='ИНН')),
                ('KPP', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(message='Введите цифры', regex='^\\d{9,15}$')], verbose_name='КПП')),
                ('legal_address', models.CharField(blank=True, max_length=250, verbose_name='Адрес фактический')),
                ('postal_address', models.CharField(blank=True, max_length=250, verbose_name='Адрес юридический')),
                ('phone_number', models.CharField(max_length=17, validators=[django.core.validators.RegexValidator(message="Телефонный номер должен быть иметь следующий формат: '+999999999'. Максимальное количество цифр 15.", regex='^\\+?1?\\d{9,15}$')], verbose_name='Номер телефона')),
                ('email_address', models.CharField(max_length=15, validators=[django.core.validators.EmailValidator()], verbose_name='Электронная почта')),
                ('is_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_update', models.DateTimeField(auto_now=True, verbose_name='Дата модификации')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, verbose_name='Наименование')),
                ('status', models.BooleanField(default=True, verbose_name='Активен')),
                ('is_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_update', models.DateTimeField(auto_now=True, verbose_name='Дата модификации')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=50, verbose_name='Наименование')),
                ('url', models.SlugField(unique=True, verbose_name='URI ресурса')),
                ('price', models.FloatField(blank=True, verbose_name='Цена')),
                ('status', models.BooleanField(default=True, verbose_name='Статус')),
                ('is_create', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('is_update', models.DateTimeField(auto_now=True, verbose_name='Дата модификации')),
                ('fk_permission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.Permission')),
            ],
        ),
        migrations.RemoveField(
            model_name='contract',
            name='customer',
        ),
        migrations.DeleteModel(
            name='Services',
        ),
        migrations.DeleteModel(
            name='Contract',
        ),
    ]
