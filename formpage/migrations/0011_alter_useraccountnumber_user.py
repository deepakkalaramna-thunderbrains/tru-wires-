# Generated by Django 4.1.4 on 2023-09-27 20:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('formpage', '0010_formtemplate_sending_account_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccountnumber',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]