# Generated by Django 4.1.4 on 2023-06-13 17:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('formpage', '0002_wireformdetails_recipient_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='formtemplate',
            name='recipient_city',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='formtemplate',
            name='recipient_state',
            field=models.CharField(choices=[('AL', 'Alabama'), ('AK', 'Alaska'), ('AZ', 'Arizona'), ('AR', 'Arkansas'), ('CA', 'California'), ('CO', 'Colorado'), ('CT', 'Connecticut'), ('DE', 'Delaware'), ('FL', 'Florida'), ('GA', 'Georgia'), ('HI', 'Hawaii'), ('ID', 'Idaho'), ('IL', 'Illinois'), ('IN', 'Indiana'), ('IA', 'Iowa'), ('KS', 'Kansas'), ('KY', 'Kentucky'), ('LA', 'Louisiana'), ('ME', 'Maine'), ('MD', 'Maryland'), ('MA', 'Massachusetts'), ('MI', 'Michigan'), ('MN', 'Minnesota'), ('MS', 'Mississippi'), ('MO', 'Missouri'), ('MT', 'Montana'), ('NE', 'Nebraska'), ('NV', 'Nevada'), ('NH', 'New Hampshire'), ('NJ', 'New Jersey'), ('NM', 'New Mexico'), ('NY', 'New York'), ('NC', 'North Carolina'), ('ND', 'North Dakota'), ('OH', 'Ohio'), ('OK', 'Oklahoma'), ('OR', 'Oregon'), ('PA', 'Pennsylvania'), ('RI', 'Rhode Island'), ('SC', 'South Carolina'), ('SD', 'South Dakota'), ('TN', 'Tennessee'), ('TX', 'Texas'), ('UT', 'Utah'), ('VT', 'Vermont'), ('VA', 'Virginia'), ('WA', 'Washington'), ('WV', 'West Virginia'), ('WI', 'Wisconsin'), ('WY', 'Wyoming'), ('OT', 'OTHER')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='formtemplate',
            name='recipient_street_address',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='formtemplate',
            name='recipient_zipcode',
            field=models.CharField(max_length=60, null=True),
        ),
    ]
