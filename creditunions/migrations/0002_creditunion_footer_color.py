# Generated by Django 4.1.4 on 2023-05-23 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('creditunions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='creditunion',
            name='footer_color',
            field=models.CharField(default='black', max_length=20),
        ),
    ]
