from django.dispatch import receiver
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import WireFormDetails, Order, Staff, Client, WireAuthorizationPair
from django.contrib.auth.models import User
from datetime import datetime
from .forms import StaffRegistrationForm

@receiver(post_save, sender=User)
def create_client_or_staff(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            print("able to create staff")
            staff = Staff.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, email=instance.email)
            staff.save()
        else:
            print("able to create staff")
            client = Client.objects.create(user=instance, first_name=instance.first_name, last_name=instance.last_name, email=instance.email)
            client.save()


@receiver(post_save, sender=WireFormDetails)
def create_order(sender, instance, created, **kwargs):
    if created:
        if instance.recurrent:
            # Handle creation of recurring orders using celery beat in tasks.py
            pass
        elif wire_needs_authorization(instance.user_id):
            # Handle creation of orders when item is authorized by appropriate party
            pass
        else:
            # Create an order for the current wire form only if recurrent is False
            order = Order.objects.create(
                client=instance.user,
                wire_details=instance,
                status='Pending',
                date_created=datetime.now().date()
            )
            order.save()

def wire_needs_authorization(user_id):
    authorizer = WireAuthorizationPair.objects.filter(sub_user_id=user_id)
    # user does not need their wireform authorized if there is no record. It can proceed normally
    if(authorizer.count() == 0):
        return False
    else:
        return True