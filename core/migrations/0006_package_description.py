# Generated by Django 2.2.3 on 2019-07-23 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20190707_0806'),
    ]

    operations = [
        migrations.AddField(
            model_name='package',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание'),
        ),
    ]