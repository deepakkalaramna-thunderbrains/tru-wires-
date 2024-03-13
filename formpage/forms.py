from unittest.mock import MagicMock
from django import forms
from django.db.models.base import Model
from django.db.models.query_utils import Q
from django.forms import ModelForm, ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import WireFormDetails, FormTemplate, Client,Order,UserAccountNumber, WireUserAmountLimit
from .choices import STATUSES,currency_choices,destination_choices,STATES,STATES_NULL,COUNTRY
from datetime import date, datetime
from recurrence.fields import RecurrenceField
from django.core.validators import RegexValidator


today = date.today()

def positive_decimal_validator(value):
    if value <= 0:
        raise forms.ValidationError("Please enter a positive amount.")
class RegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )
        help_texts = {
            'username': None,
            'email': None,
        }

class StaffRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    email = forms.EmailField(max_length=150)
    job_title = forms.CharField(max_length=100)
    department = forms.CharField(max_length=100)


    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1','job_title','department', 'password2', )
        help_texts = {
            'username': None,
            'email': None,
        }

class UserAccountNumberField(forms.ModelChoiceField):
     def label_from_instance(self, obj:UserAccountNumber) -> str:
          return obj.account_number

class WireForm(forms.ModelForm):
        name            = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Template Name')
                        }
                    ),
                         required=False
                )
        destination                 = forms.ChoiceField(
            widget=forms.RadioSelect(attrs={'id': 'value'}),
            choices=destination_choices,
            )
        currency                 = forms.ChoiceField(
            widget=forms.RadioSelect(attrs={'id': 'value'}),
            choices=currency_choices
            )
        currency_name          = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Currency Name')
                        }
                    ),
                         required=False
                )
        recurrent = forms.BooleanField( 
              widget=forms.widgets.CheckboxInput( attrs={'class': 'checkbox-inline'})
              )
        
        sending_businessname = forms.CharField(                
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('Business Name')
                    }
                ),
                required=True
            )
        

        sending_street_address = forms.CharField(                
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('Business Address')
                    }
                ),
                    required=True
            )
        
        sending_city = forms.CharField(                
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('Business City')
                    }
                ),
                    required=True
            )
        sending_state = forms.ChoiceField(
             choices=STATES,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('State')
                        }
                    ),
                         required=True
                )

        sending_zipcode = forms.CharField(
             max_length=5,
             validators=[RegexValidator('^[0-9]{5}$',('Invalid ZIP CODE'))],
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Zip Code')
                        }
                    ),
                         required=True
                )
                
        sending_account_number = UserAccountNumberField(UserAccountNumber.objects, required=True, empty_label="Select Account Number")
        
        sending_account_type = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Sending Account Type')
                        }
                    ),
                         required=True
                )
        
        sending_amount = forms.DecimalField(
                widget=forms.NumberInput(
                    attrs={
                        'placeholder': ('Amount')
                        }
                    ),
                         required=True,
                         validators=[positive_decimal_validator]
                )
        
        effective_date = forms.DateField(
                widget=forms.TextInput(
                    attrs={
                        'value': today, 'type': 'date'
                        }
                        ),
                         required=True
                 )
        recurrent                   = RecurrenceField(null=True)
        recipient_name = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Recipient Name')
                        }
                    ),
                         required=True
                )
        
        recipient_account_type = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Recipient Account Type')
                        }
                    )
                )
        
        recipient_account_number = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Recipient Account Number')
                        }
                    ),
                         required=True
                )
        
        
        recipient_routing_number = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Recipient Routing Number')
                        }
                    )
                )
        recipient_street_address = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('Street Address')
                    }
                )
            )
        recipient_city = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('City')
                    }
                )
            )
        recipient_state = forms.ChoiceField(
             choices=STATES,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('State')
                        }
                    ),
                         required=True
                )
        recipient_zipcode = forms.CharField(
            widget=forms.TextInput(
                attrs={
                    'placeholder': ('Zip code')
                    }
                )
                )
        receiving_bank_name = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Bank Name')
                        }
                    ),
                         required=False
                )
        receiving_street_address = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Street Address')
                        }
                    ),
                         required=False
                )
        receiving_bank_city = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('City')
                        }
                    ),
                         required=False
                )
        receiving_bank_state = forms.ChoiceField(
             choices=STATES_NULL,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('State')
                        }
                    ),
                         required=False
                )
        
        receiving_bank_zipcode = forms.CharField(
             max_length=20,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Zip Code')
                        }
                    ),
                         required=False
                )
        
        intermediary_bank_name = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Bank Name')
                        }
                    ),
                    required=False
                )
        
        intermediary_bank_st_adress = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Street Address')
                        }
                    ),
                    required=False
                )
        
        intermediary_bank_country = forms.ChoiceField(
            widget=forms.RadioSelect(attrs={'id': 'value'}),
            choices=COUNTRY,
            required=False,
            initial='',

            )
        intermediary_bank_country_name = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Country')
                        }
                    ),
                    required=False
                )
        
        intermediary_bank_state =  forms.ChoiceField(
             choices=STATES_NULL,
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('State')
                        }
                    ),
                         required=False
                )
        
        intermediary_bank_post_code = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Bank Zip')
                        }
                    ),
                    required=False
                )
        
        intermediary_routing_number =  forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Intermediary Routing Number')
                        }
                    ),
                    required=False
                )
        
        intermediary_bank_swift = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('SWIFT')
                        }
                    ),
                    required=False
                )
        
        intermediary_bank_iban = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('IBAN')
                        }
                    ),
                    required=False
                )
        
        purpose_of_wire = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Purpose')
                        }
                    ),
                         required=True
                )
        
        description = forms.CharField(
                widget=forms.TextInput(
                    attrs={
                        'placeholder': ('Description')
                        }
                    ),
                    required=False
                )

        class Meta:
            model = WireFormDetails
            exclude= ['user']

        def __init__(self, *args, **kwargs):
            user_id = kwargs.pop('user_id', None)
            super(WireForm, self).__init__(*args, **kwargs)

            # Customize the queryset for the author field based on the provided author_id
            if user_id is not None:
                self.fields['sending_account_number'].queryset = UserAccountNumber.objects.filter(user_id=user_id)
        
        def clean_sending_amount(self):
            sending_amount = self.cleaned_data["sending_amount"]
            sending_account_number = self.cleaned_data['sending_account_number']
            client = sending_account_number.user.client
            if hasattr(client, 'wireuseramountlimit') and sending_amount > client.wireuseramountlimit.max_amount:
                raise ValidationError("The requested wire submission exceeds your approved limits.  Please contact your administrator for approval and resubmit request.")
            return sending_amount





class WireFormTemplate(ModelForm):

        class Meta:
            model = FormTemplate
            fields = '__all__'
        # def __init__(self, *args, **kwargs):
        #     #using kwargs
        #     user = kwargs.pop('user', None)
        #     super(WireFormTemplate, self).__init__(*args, **kwargs)
        #     self.fields['user'].queryset = User.objects.filter(pk = user.id)
        #     print("user is ", user)

class OrderForm(forms.ModelForm):
    

    class Meta:
        model = Order
        fields = ('status',)
