from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from recurrence.fields import RecurrenceField
from django.core.validators import RegexValidator
from datetime import datetime

from .choices import currency_choices, destination_choices, STATES, STATES_NULL, STATUSES,COUNTRY

current_date = datetime.now().date()




class Client(models.Model):
    user = models.OneToOneField(User, null=True,on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField( max_length=150)
    signup_confirmation = models.BooleanField(default=False)
    

    def __str__(self):
        return  '%s'%(self.user)




class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    job_title = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField(max_length=150)
    signup_confirmation = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return  '%s'%(self.user)
    
# @receiver(post_save, sender=User)
# def create_staff(sender, instance, created, **kwargs):
#     if created and not hasattr(instance, 'client'):
#         staff = Staff.objects.create(user=instance)
#         staff.save()
class UserAccountNumber(models.Model):
    user                             = models.ForeignKey(User,null=True,  on_delete=models.CASCADE)
    account_number                   = models.CharField(max_length=60)
    def __str__(self):
        display = self.user.username + " - " + self.account_number
        return  '%s'%(display)

class WireFormDetails(models.Model):
    user                             = models.ForeignKey(Client, null=True, on_delete=models.CASCADE)
    destination                      = models.CharField(choices=destination_choices,null=True, max_length=20)
    currency                         = models.CharField(choices=currency_choices,null=True, max_length=40)
    recurrent                        = models.BooleanField(default=False)
    recurrency                       = RecurrenceField(blank=True,null=True)
    sending_account_number           = models.ForeignKey(UserAccountNumber,null=True, on_delete=models.DO_NOTHING)
    sending_account_type             = models.CharField(max_length=60)
    sending_amount                   = models.DecimalField(max_digits=10, default=00, decimal_places=2)
    sending_businessname             = models.CharField(max_length=60,null=True)
    sending_street_address           = models.CharField(max_length=60,null=True)
    sending_city                     = models.CharField(max_length=60,null=True)
    sending_state                    = models.CharField(choices=STATES,null=True,max_length=20)
    sending_zipcode                  = models.CharField(max_length=60,null=True)
    effective_date                   = models.DateField()
    recipient_name                   = models.CharField(max_length=60)
    recipient_account_type           = models.CharField(max_length=60)
    recipient_account_number         = models.CharField(max_length=60)
    recipient_routing_number         = models.CharField(max_length=60)
    recipient_street_address         = models.CharField(max_length=60,null=True)
    recipient_city                   = models.CharField(max_length=60,null=True)
    recipient_state                  = models.CharField(choices=STATES,null=True,max_length=20)
    recipient_zipcode                = models.CharField(max_length=60,null=True)
    receiving_bank_name              = models.CharField(max_length=60)
    receiving_street_address         = models.CharField(max_length=60) 
    receiving_bank_city            = models.CharField(max_length=60,null=True) 
    receiving_bank_state             = models.CharField(choices=STATES_NULL,max_length=20, null=True)
    receiving_bank_zipcode           = models.CharField(max_length=20,null=True)
    intermediary_bank_name           = models.CharField(max_length=60,null=True)
    intermediary_bank_st_adress      = models.CharField(max_length=60,null=True) 
    intermediary_bank_country        = models.CharField(choices=COUNTRY,null=True,max_length=20)
    intermediary_bank_state          = models.CharField(choices=STATES_NULL,null=True,max_length=20)
    intermediary_bank_country_name   = models.CharField(max_length=20,null=True)
    intermediary_bank_post_code      = models.CharField(max_length=20,null=True)
    intermediary_routing_number      = models.CharField(max_length=60,null=True)
    intermediary_bank_swift          = models.CharField(max_length=20,null=True)
    intermediary_bank_iban           = models.CharField(max_length=40,null=True)
    purpose_of_wire                  = models.CharField(max_length=100)
    description                      = models.TextField(max_length=100)
    created_at                       = models.DateTimeField(auto_now_add=True,null=True)

    def __str__(self):
        return f'{self.user} - {self.destination} - {self.effective_date}'
    slug = models.SlugField(
        default="", editable=False, max_length=settings.WIRE_TITLE_MAX_LENGTH
    )
    def slug_length(self):
        return len(str(self.id)) + 1 + len(self.slug)
   


class Order(models.Model): 
    client          = models.ForeignKey(Client,  on_delete=models.CASCADE)
    wire_details    = models.ForeignKey(WireFormDetails,  on_delete=models.CASCADE)
    date_created    = models.DateTimeField(auto_now_add=True)
    status          = models.CharField(max_length=200, choices=STATUSES)
    
    def __str__(self):
        return f'{self.client} - {self.wire_details} - {self.status}'
    def update_wire_details(self, destination):
        wire_details = self.order
        wire_details.destination = destination
        wire_details.save()
    
class WireAuthorizationPair(models.Model):
    authorizer = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    sub_user = models.ForeignKey(Client, null=False, on_delete=models.CASCADE)   
    def __str__(self):
            display = 'Authorizer: ' + self.authorizer.username + " - Sub User: " + self.sub_user.user.username
            return  '%s'%(display)
    class Meta:
        unique_together = ['authorizer', 'sub_user']

class WireAuthorization(models.Model):
    wire_details = models.ForeignKey(WireFormDetails, null=False,on_delete=models.CASCADE, related_name='wire_authorizations')
    authorization_pair = models.ForeignKey(WireAuthorizationPair, null=False, on_delete=models.CASCADE)
    authorized = models.BooleanField(null=True, default=None)
    def __str__(self):
        auth = ''
        if(self.authorized is None):
            auth = 'Awaiting Authorization'
        elif(self.authorized):
            auth = 'Authorized'
        else:
            auth = 'Rejected'
        return f'Authorizer: {self.authorization_pair.authorizer.username} Wire Details: {self.wire_details} Status: {auth}'
    class Meta:
        unique_together = ['wire_details', 'authorization_pair']

class WireUserAmountLimit(models.Model):
    user     = models.OneToOneField(Client, on_delete=models.CASCADE)
    max_amount = models.DecimalField(max_digits=10, default=00, decimal_places=2)
    def __str__(self):
        return f'{self.user} - ${self.max_amount}'

class ReccurentOrder(models.Model): 
    client          = models.ForeignKey(Client,  on_delete=models.CASCADE)
    wire_details    = models.ForeignKey(WireFormDetails,  on_delete=models.CASCADE)
    date_created    = models.DateTimeField(auto_now_add=True)
    status          = models.CharField(max_length=200, choices=STATUSES)
    
    def __str__(self):
        return f'{self.client} - {self.wire_details} - {self.status}'
    def update_wire_details(self, destination):
        wire_details = self.order
        wire_details.destination = destination
        wire_details.save()


class FormTemplate(models.Model):
    user                             = models.ForeignKey(Client,null=True,  on_delete=models.CASCADE)
    name                             = models.CharField( max_length=30)
    destination                      = models.CharField(choices=destination_choices, max_length=20)
    currency                         = models.CharField(choices=currency_choices, max_length=40)
    sending_account_number           = models.ForeignKey(UserAccountNumber,null=True, on_delete=models.DO_NOTHING)
    sending_account_type             = models.CharField(max_length=60)
    sending_amount                   = models.DecimalField(max_digits=10, default=00, decimal_places=2)
    sending_businessname             = models.CharField(max_length=60,null=True)
    sending_street_address           = models.CharField(max_length=60,null=True)
    sending_city                     = models.CharField(max_length=60,null=True)
    sending_state                    = models.CharField(choices=STATES,null=True,max_length=20)
    sending_zipcode                  = models.CharField(max_length=60,null=True)
    effective_date                   = models.DateField()
    recurrent                        = models.BooleanField(default=False)
    recurrency                       = RecurrenceField(blank=True,null=True)
    recipient_name                   = models.CharField(max_length=60)
    recipient_account_type           = models.CharField(max_length=60)
    recipient_account_number         = models.CharField(max_length=60)
    recipient_routing_number         = models.CharField(max_length=60)
    recipient_street_address         = models.CharField(max_length=60,null=True)
    recipient_city                   = models.CharField(max_length=60,null=True)
    recipient_state                  = models.CharField(choices=STATES,null=True,max_length=20)
    recipient_zipcode                = models.CharField(max_length=60,null=True)
    receiving_bank_name              = models.CharField(max_length=60)
    receiving_street_address         = models.CharField(max_length=60)
    receiving_bank_city              = models.CharField(max_length=60,null=True) 
    receiving_bank_state             = models.CharField(choices=STATES_NULL,max_length=60, null=True)
    receiving_bank_zipcode           = models.CharField(max_length=20,null=True)
    intermediary_bank_name           = models.CharField(max_length=60,null=True)
    intermediary_bank_st_adress      = models.CharField(max_length=60,null=True) 
    intermediary_bank_country        = models.CharField(choices=COUNTRY,null=True,max_length=20)
    intermediary_bank_country_name   = models.CharField(max_length=20,null=True)
    intermediary_bank_state          = models.CharField(choices=STATES_NULL,null=True,max_length=20)
    intermediary_bank_post_code      = models.CharField(max_length=20,null=True)
    intermediary_routing_number      = models.CharField(max_length=60,null=True)
    intermediary_bank_swift          = models.CharField(max_length=20,null=True)
    intermediary_bank_iban           = models.CharField(max_length=40,null=True)
    purpose_of_wire                  = models.CharField(max_length=100)
    description                      = models.TextField(max_length=100)
    created_at    = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user} - {self.destination} - {self.effective_date}'


