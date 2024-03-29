# Generated by Django 4.1.4 on 2023-11-28 21:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('formpage', '0012_alter_formtemplate_intermediary_bank_country_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WireUserAmountLimit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('max_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='formpage.client')),
            ],
        ),
    ]
