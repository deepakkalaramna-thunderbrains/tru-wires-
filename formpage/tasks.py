from celery import shared_task
from django.utils import timezone
from dateutil.rrule import rrulestr
from dateutil.tz import UTC
from datetime import datetime, timedelta
from .models import WireFormDetails, Order

@shared_task
def create_recurring_orders():
    order_form_details = WireFormDetails.objects.all()
    for order_form_detail in order_form_details:
        if order_form_detail.recurrent:
                # Get all WireFormDetails objects with recurrent and recurrency set
                wire_forms = WireFormDetails.objects.filter(recurrent=True).exclude(recurrency=None)
                current_date = datetime.now().date()
                
                for wire_form in wire_forms:
                    recurrence_str = str(wire_form.recurrency)
                    start_date = wire_form.created_at.replace(tzinfo=UTC)
                    rrule = rrulestr(recurrence_str, dtstart=start_date)
                    
                    # Check if the rule applies for the current day
                    if rrule._byweekday and timezone.now().weekday() not in rrule._byweekday:
                        continue
                    
                    # Check if the rule applies for the current week
                    if rrule._byweekno and timezone.now().isocalendar()[1] not in rrule._byweekno:
                        continue
                    
                    # Check if the rule applies for the current month
                    if rrule._bymonthday and timezone.now().day not in rrule._bymonthday:
                        continue
                    
                    # Check if an order already exists for the current day, week, or month
                    existing_order = None
                    if rrule._byweekday:
                        # For weekly recurrence, check if an order exists for the current week
                        week_start = timezone.now().date() - timedelta(days=timezone.now().weekday())
                        week_end = week_start + timedelta(days=6)
                        existing_order = Order.objects.filter(wire_details=wire_form, date_created__range=[week_start, week_end]).first()
                    elif rrule._bymonthday:
                        # For monthly recurrence, check if an order exists for the current month
                        month_start = timezone.now().date().replace(day=1)
                        month_end = month_start + timedelta(days=31)
                        existing_order = Order.objects.filter(wire_details=wire_form, date_created__range=[month_start, month_end]).first()
                    else:
                        # For daily recurrence, check if an order exists for the current day
                        existing_order = Order.objects.filter(wire_details=wire_form, date_created=current_date).first()
                    
                    # Create a new order only if no existing order was found
                    if not existing_order:
                        order = Order.objects.create(
                            client=wire_form.user,
                            wire_details=wire_form,
                            status='Pending',
                            date_created=current_date
                        )
                        order.save()
