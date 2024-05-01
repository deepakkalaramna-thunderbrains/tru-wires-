from pathlib import Path
from smtplib import SMTPException
from django.shortcuts import render, redirect,get_object_or_404
from django.template.loader import get_template, render_to_string
from django.views.generic import  ListView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import message, send_mail,get_connection, EmailMessage, EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.http.response import BadHeaderError
from django.db import IntegrityError
from django.urls import reverse,reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.views.generic import CreateView
from django.views.generic.edit import ModelFormMixin

from dateutil.rrule import rrulestr
from datetime import date, datetime, timedelta

from .choices import STATUSES,currency_choices,destination_choices,STATES,STATES_NULL,COUNTRY

from .decorators import  client_required,staff_only
from .forms   import WireForm, RegistrationForm, FormTemplate,WireFormTemplate,OrderForm,StaffRegistrationForm
from .models  import UserAccountNumber, WireFormDetails,Order,ReccurentOrder,Client,Staff, WireAuthorizationPair, WireAuthorization
from .tokens  import account_activation_token
from wireform import settings  
from django_pgschemas.utils import get_tenant_model,get_domain_model
import io
import xlsxwriter

# Create your views here.
def activation_sent_view(request):
    return render(request,'accounts/activation_sent.html')

def registerDoaminUser(request):
    return('api hitted successfully..')

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        if user.is_staff:
            if(not hasattr(user, 'staff')):
                user.staff = Staff.objects.create(user=user, first_name=user.first_name, last_name=user.last_name, email=user.email, is_approved=True)
            user.staff.signup_confirmation = True
            user.staff.save() 
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('dashboard')
        else:
            user.client.signup_confirmation = True
            user.client.save() 
            user.is_active = True
            user.save()
            login(request, user)
            return redirect('home')

    else:
        return render(request, 'accounts/activation_invalid.html')






def register(request):
    form = RegistrationForm()
    context = {'form':form}
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context={'form':form }
        if form.is_valid():
            input_email = form.cleaned_data.get('email')
            for instance in Client.objects.all():
                if instance.email == input_email:
                    messages.warning(request,'Email with ' + input_email + ' is already registered with us please use another email!')
                    return render(request,'accounts/signup.html',context)
            user = form.save()
            user.is_active = False
            if(user.username == settings.NEW_CREDITUNION_ADMIN):
                user.is_staff = True
                user.is_superuser = True
            else: 
                user.is_staff = False
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            from_email = settings.EMAIL_HOST_USER
            to_email   = form.cleaned_data.get('email')
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                #  generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            email= EmailMessage(
                subject,
                message,
                from_email,
                [to_email],
             
            )
            email.content_subtype =  'html'
            try:
                email.send(fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid Header found.')
            return redirect('activation_sent')

        else:
            form    = RegistrationForm()
    return render(request,'accounts/signup.html',context)

def staff_registration(request):
    form = StaffRegistrationForm()
    context = {'form':form}
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        context={'form':form }
        if form.is_valid():
            input_email = form.cleaned_data.get('email')
            for instance in Staff.objects.all():
                if instance.email == input_email:
                    messages.warning(request,'Email Address' + input_email + ' is already registered with us please use another email!')
                    return render(request,'accounts/signup.html',context)
            user = form.save(commit=False)
            user.is_active = False
            user.is_staff = True
            user.save()
            current_site = get_current_site(request)
            subject = 'Please Activate Your Account'
            from_email = settings.EMAIL_HOST_USER
            to_email   = form.cleaned_data.get('email')
            message = render_to_string('accounts/activation_request.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                #  generate a hash value with user related data
                'token': account_activation_token.make_token(user),
            })
            email= EmailMessage(
                subject,
                message,
                from_email,
                [to_email],
             
            )
            email.content_subtype =  'html'
            try:
                email.send(fail_silently=False)
            except BadHeaderError:
                return HttpResponse('Invalid Header found.')
            return redirect('activation_sent')

        else:
            form    = StaffRegistrationForm()
    return render(request,'accounts/staff_signup.html',context)





def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if hasattr(user, 'staff'):
                return redirect('dashboard')
            else:
                return redirect('home')
        else:
            messages.info(request, 'Incorrect username or password')
    
    return render(request, 'accounts/login.html')


def logout_page(request):
    logout(request)
    return redirect('login')




 
@login_required(login_url='login')
@client_required
def index(request):
    form    = WireForm(request.POST or None,user_id=request.user.id)
    form.fields['effective_date'].initial = datetime.today().date()
    allow_international_wires = does_credit_union_allow_international_wires(request)
    context =  {'form': form, 'allow_international_wires': allow_international_wires}        
    return render(request, 'wireform.html',context) 

@login_required(login_url='login')
@client_required
def submit_wire_info(request):
    form = WireForm(request.POST)
    if form.is_valid():
        user                        =  request.user.client
        destination                 =  form.cleaned_data['destination']
        currency                    =  form.cleaned_data['currency']
        recurrent                   =  form.cleaned_data['recurrent']
        recurrency                  =  form.cleaned_data['recurrency']
        sending_account_number      =  form.cleaned_data['sending_account_number']
        sending_account_type        =  form.cleaned_data['sending_account_type']
        sending_amount              =  form.cleaned_data['sending_amount']
        sending_businessname        =  form.cleaned_data['sending_businessname']
        sending_street_address      =  form.cleaned_data['sending_street_address']
        sending_city                =  form.cleaned_data['sending_city']
        sending_state               =  form.cleaned_data['sending_state']
        sending_zipcode             =  form.cleaned_data['sending_zipcode']
        effective_date              =  form.cleaned_data['effective_date']
        recipient_name              =  form.cleaned_data['recipient_name']
        recipient_account_type      =  form.cleaned_data['recipient_account_type']
        recipient_account_number    =  form.cleaned_data['recipient_account_number']
        recipient_routing_number    =  form.cleaned_data['recipient_routing_number']
        recipient_street_address    =  form.cleaned_data['recipient_street_address']
        recipient_city              =  form.cleaned_data['recipient_city']
        recipient_state             =  form.cleaned_data['recipient_state']
        recipient_zipcode           =  form.cleaned_data['recipient_zipcode']
        receiving_bank_name         =  form.cleaned_data['receiving_bank_name']
        receiving_street_address    =  form.cleaned_data['receiving_street_address']
        receiving_bank_city         =  form.cleaned_data['receiving_bank_city']
        receiving_bank_state        =  form.cleaned_data['receiving_bank_state']
        receiving_bank_zipcode      =  form.cleaned_data['receiving_bank_zipcode']
        intermediary_bank_name      =  form.cleaned_data['intermediary_bank_name']
        intermediary_bank_st_adress =  form.cleaned_data['intermediary_bank_st_adress']
        intermediary_bank_country   =  form.cleaned_data['intermediary_bank_country']
        intermediary_bank_state      =  form.cleaned_data['intermediary_bank_state']
        intermediary_bank_country_name   =  form.cleaned_data['intermediary_bank_country_name']
        intermediary_bank_post_code =  form.cleaned_data['intermediary_bank_post_code']
        intermediary_bank_swift     =  form.cleaned_data['intermediary_bank_swift']
        intermediary_bank_iban      =  form.cleaned_data['intermediary_bank_iban']
        intermediary_routing_number =  form.cleaned_data['intermediary_routing_number']
        purpose_of_wire             =  form.cleaned_data['purpose_of_wire']
        description                 =  form.cleaned_data['description']
        wire_info = WireFormDetails(user=user,destination=destination,currency=currency,recurrent=recurrent,recurrency=recurrency,sending_account_number=sending_account_number,sending_account_type=sending_account_type,sending_amount=sending_amount,sending_businessname=sending_businessname,sending_street_address=sending_street_address,sending_city=sending_city,sending_state=sending_state,sending_zipcode=sending_zipcode,effective_date=effective_date,recipient_name=recipient_name,recipient_account_type=recipient_account_type,recipient_account_number=recipient_account_number,recipient_routing_number=recipient_routing_number,recipient_street_address=recipient_street_address,recipient_city=recipient_city,recipient_state=recipient_state,recipient_zipcode=recipient_zipcode,receiving_bank_name=receiving_bank_name,receiving_street_address=receiving_street_address,receiving_bank_city=receiving_bank_city,receiving_bank_state=receiving_bank_state,receiving_bank_zipcode=receiving_bank_zipcode,intermediary_bank_name=intermediary_bank_name,intermediary_bank_st_adress=intermediary_bank_st_adress,intermediary_bank_country=intermediary_bank_country,intermediary_bank_state=intermediary_bank_state,intermediary_bank_country_name=intermediary_bank_country_name,intermediary_bank_post_code=intermediary_bank_post_code,intermediary_bank_swift=intermediary_bank_swift,intermediary_bank_iban=intermediary_bank_iban,intermediary_routing_number=intermediary_routing_number,purpose_of_wire=purpose_of_wire,description=description     
        )
        
        wire_info.save()
        request.session['wire_info_id'] = wire_info.id
        order_id = request.session.get('wire_info_id')
        return redirect('order_confirmation')
    form.fields['sending_account_number'].queryset = UserAccountNumber.objects.filter(user_id=request.user.id)
    return render(request, "wireform.html",{'form': form})

@login_required(login_url='login')  
@client_required
def order_confirmation(request):
    order_id = request.session.get('wire_info_id')
    if not order_id:
        messages.error(request, 'There was an error processing your order.')
        return render(request, "wireform.html")
    order = WireFormDetails.objects.get(id=order_id)
    order.sending_state_view = get_full_state_by_abbreviation(order.sending_state)
    order.recipient_state_view = get_full_state_by_abbreviation(order.recipient_state)
    order.receiving_bank_state_view = get_full_state_by_abbreviation(order.receiving_bank_state)
    order.intermediary_bank_state_view = get_full_state_by_abbreviation(order.intermediary_bank_state)
    order.intermediary_bank_country_view = get_full_country_by_abbreviation(order.intermediary_bank_country)

    
    if request.method == 'POST':
        if 'confirm' in request.POST:
            messages.success(request, 'Order confirmed')
            del request.session['wire_info_id']
            order.confirmed = True
            order.save()
            notify_users_of_wire_submission(request,order)
            return redirect('wire_requests')
        elif 'cancel' in request.POST:
            order.delete()
            del request.session['wire_info_id']
            messages.warning(request, 'Order cancelled')
            return redirect('home')
    return render(request, 'confirm_order.html', {'order': order})

    
@login_required(login_url='login') 
def render_entries(request):
    if request.user.is_staff:
        order = Order.objects.all().order_by('-date_created')
    else:
        order = request.user.client.order_set.all().order_by('-date_created')
    context ={'order':order}
    return render(request, "last_entry.html",context)


@login_required(login_url='login') 
def monthly_report(request):
    order = Order.objects.filter(
        wire_details__effective_date__range=('2024-01-01', '2024-01-31'),
        status='Approved'
            )
    context ={'order':order}
    print(order,)

    return render(request, "monthly_report.html", context)


@login_required(login_url='login') 
def download_monthly_report(request):
    order = Order.objects.filter(
        wire_details__effective_date__range=('2024-01-01', '2024-01-31'),
        status='Approved'
    )
    output = io.BytesIO()

    # Create a new Excel workbook
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()

    # Write headers
    headers = [
        'Sending Business Name', 
        'Sending Account Number', 
        'Sending Account Type', 
        'ID', 
        'Effective Date', 
        'Recipient Name', 
        'Sending Amount', 
        'Currency', 
        'Intermediary Bank Country', 
        'Status'
    ]
    for col, header in enumerate(headers):
        worksheet.write(0, col, header)

    # Write data rows
    row = 1
    for order in order:
        worksheet.write(row, 0, order.wire_details.sending_businessname)
        worksheet.write(row, 1, order.wire_details.sending_account_number.account_number)
        worksheet.write(row, 2, order.wire_details.sending_account_type)
        worksheet.write(row, 3, order.id)
        worksheet.write(row, 4, order.wire_details.effective_date)
        worksheet.write(row, 5, order.wire_details.recipient_name)
        worksheet.write(row, 6, order.wire_details.sending_amount)
        worksheet.write(row, 7, order.wire_details.currency)
        worksheet.write(row, 8, order.wire_details.intermediary_bank_country)
        worksheet.write(row, 9, order.status)
        row += 1

    # Close the workbook
    workbook.close()

    # Set up response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=monthly_report.xlsx'

    # Write the workbook data to the response
    output.seek(0)
    response.write(output.getvalue())

    return response

@login_required(login_url='login') 
def render_authorization_entries(request):
    is_authorizer = False
    open_orders = WireAuthorization.objects.filter(authorized=None)
    if is_user_authorizer(request.user.id):
        order = WireAuthorization.objects.filter(authorization_pair__authorizer=request.user)
        is_authorizer = True
    elif is_user_sub_user(request.user.client.id):
        order = WireAuthorization.objects.filter(authorization_pair__sub_user=request.user.client)
    else:
        return redirect('/index.html') 
    context ={'order':order & open_orders, 'is_authorizer': is_authorizer}
    return render(request, "authorization_entries.html",context)

@login_required(login_url='login') 
def authorize_wire(request,pk):
    wire_authorization = WireAuthorization.objects.filter(id=pk).first()
    order = Order(wire_details=wire_authorization.wire_details, 
                         client=wire_authorization.wire_details.user, 
                         date_created=wire_authorization.wire_details.created_at, 
                         status='Pending')
    order.save()
    wire_authorization.authorized = True
    wire_authorization.save()
    send_order_confirmation_email(request, order.wire_details)
    return redirect('/authorization') 

@login_required(login_url='login') 
def reject_unauthorized_wire(request,pk):
    wire_authorization = WireAuthorization.objects.filter(id=pk).first()
    order = Order(wire_details=wire_authorization.wire_details, 
                         client=wire_authorization.wire_details.user, 
                         date_created=wire_authorization.wire_details.created_at, 
                         status='Rejected')
    order.save()
    wire_authorization.authorized = False
    wire_authorization.save()
    send_order_confirmation_email(request, order.wire_details)
    return redirect('/authorization') 


class render_authorization_entry_view(DetailView):
    model = WireAuthorization
    query_pk_and_slug = True
    template_name = "authorization_entry.html"
    
    def get_object(self):
        obj = super().get_object()
        obj.wire_details.sending_state = get_full_state_by_abbreviation(obj.wire_details.sending_state)
        obj.wire_details.recipient_state = get_full_state_by_abbreviation(obj.wire_details.recipient_state)
        obj.wire_details.receiving_bank_state = get_full_state_by_abbreviation(obj.wire_details.receiving_bank_state)
        obj.wire_details.intermediary_bank_state = get_full_state_by_abbreviation(obj.wire_details.intermediary_bank_state)
        obj.wire_details.intermediary_bank_country = get_full_country_by_abbreviation(obj.wire_details.intermediary_bank_country)
        return obj

class render_entry_view(DetailView):
    model = Order
    query_pk_and_slug = True
    template_name = "wire_entry.html"
    def get(self,request, *args, **kwargs):
        order_id = kwargs['pk']
        order = Order.objects.filter(id=order_id).first()
        if(order is None or (not self.request.user.is_staff and self.request.user.client != order.client)):
            return redirect('/submit_order/last_entry') 
        elif(self.request.user.is_staff or self.request.user.client == order.client):
            order.wire_details.sending_state = get_full_state_by_abbreviation(order.wire_details.sending_state)
            order.wire_details.recipient_state = get_full_state_by_abbreviation(order.wire_details.recipient_state)
            order.wire_details.receiving_bank_state = get_full_state_by_abbreviation(order.wire_details.receiving_bank_state)
            order.wire_details.intermediary_bank_state = get_full_state_by_abbreviation(order.wire_details.intermediary_bank_state)
            order.wire_details.intermediary_bank_country = get_full_country_by_abbreviation(order.wire_details.intermediary_bank_country)
            return render(request, "wire_entry.html", {'object':order})              
                       

class CloneView(DetailView):
    model = Order
    query_pk_and_slug = True
    template_name = "clone_form.html"

    def get_context_data(self, **kwargs):
        context = super(CloneView, self).get_context_data(**kwargs)
        form = WireForm(user_id=self.object.wire_details.user_id)
        context['form'] = form
        return context
        
    # def submit_cloned_wire_info(self, request, *args, **kwargs):
    

@login_required(login_url='login')  
@client_required
def submit_cloned_wire_info(request):
    if request.method == 'POST':
        user                        =  request.user.client
        destination                 =  request.POST.get('destination')
        currency                    =  request.POST.get('currency')
        sending_account_number      =  request.POST.get('sending_account_number')
        sending_account_number      =  UserAccountNumber.objects.filter(id=sending_account_number).first()
        sending_account_type        =  request.POST.get('sending_account_type')
        sending_amount              =  request.POST.get('sending_amount')
        sending_businessname        =  request.POST.get('sending_businessname')
        sending_street_address      =  request.POST.get('sending_street_address')
        sending_city                =  request.POST.get('sending_city')
        sending_state               =  request.POST.get('sending_state')
        sending_zipcode             =  request.POST.get('sending_zipcode')
        effective_date              =  request.POST.get('effective_date')
        # effective_date              = datetime.strptime(date, "%b. %d, %Y")
        recipient_name              =  request.POST.get('recipient_name')
        recipient_account_type      =  request.POST.get('recipient_account_type')
        recipient_account_number    =  request.POST.get('recipient_account_number')
        recipient_routing_number    =  request.POST.get('recipient_routing_number')
        recipient_street_address    =  request.POST.get('recipient_street_address')
        recipient_city              =  request.POST.get('recipient_city')
        recipient_state             =  request.POST.get('recipient_state')
        recipient_zipcode           =  request.POST.get('recipient_zipcode')
        receiving_bank_name         =  request.POST.get('receiving_bank_name')
        receiving_street_address    =  request.POST.get('receiving_street_address')
        receiving_bank_state        =  request.POST.get('receiving_bank_state')
        receiving_bank_city         =  request.POST.get('receiving_bank_city')
        receiving_bank_zipcode      =  request.POST.get('receiving_bank_zipcode')
        intermediary_bank_name      =  request.POST.get('intermediary_bank_name')
        intermediary_bank_st_adress =  request.POST.get('intermediary_bank_st_adress')
        intermediary_bank_country   =  request.POST.get('intermediary_bank_country')
        intermediary_bank_post_code =  request.POST.get('intermediary_bank_post_code')
        intermediary_bank_state     =  request.POST.get('intermediary_bank_state')
        intermediary_bank_swift     =  request.POST.get('intermediary_bank_swift')
        intermediary_bank_iban      =  request.POST.get('intermediary_bank_iban')
        intermediary_routing_number =  request.POST.get('intermediary_routing_number')
        purpose_of_wire             =  request.POST.get('purpose_of_wire')
        description                 =  request.POST.get('description')
        cloned_wire_info = WireFormDetails(user=user,destination=destination,currency=currency,sending_account_number=sending_account_number,sending_account_type=sending_account_type,sending_amount=sending_amount,sending_businessname=sending_businessname,sending_street_address=sending_street_address,sending_city=sending_city,sending_state=sending_state,sending_zipcode=sending_zipcode,effective_date=effective_date,recipient_name=recipient_name,recipient_account_type=recipient_account_type,recipient_account_number=recipient_account_number,recipient_routing_number=recipient_routing_number,recipient_street_address=recipient_street_address,recipient_city=recipient_city,recipient_state=recipient_state,recipient_zipcode=recipient_zipcode,receiving_bank_name=receiving_bank_name,receiving_street_address=receiving_street_address,receiving_bank_city=receiving_bank_city,receiving_bank_state=receiving_bank_state,receiving_bank_zipcode=receiving_bank_zipcode,intermediary_bank_name=intermediary_bank_name,intermediary_bank_st_adress=intermediary_bank_st_adress,intermediary_bank_country=intermediary_bank_country,
        intermediary_bank_post_code=intermediary_bank_post_code,intermediary_bank_state=intermediary_bank_state,intermediary_bank_swift=intermediary_bank_swift,intermediary_bank_iban=intermediary_bank_iban,intermediary_routing_number=intermediary_routing_number,purpose_of_wire=purpose_of_wire,description=description  )
        cloned_wire_info.save()
        notify_users_of_wire_submission(request, cloned_wire_info)        
    
    return render(request, "success.html")   



@login_required(login_url='login') 
@client_required
def get_form_templates(request):
    templates = request.user.client.formtemplate_set.all()
    context = {'templates':templates}

    return render(request,"formTemplates/templates_list.html",context)

@login_required(login_url='login')
@client_required
def create_template(request):
    show_element = True
    reccurency_instructions = False
    reccurency_feilds       = False
    form = WireForm(user_id=request.user.id)
    allow_international_wires = does_credit_union_allow_international_wires(request)
    context = {'form':form,'show_element':show_element,'reccurency_instructions':reccurency_instructions,'reccurency_feilds':reccurency_feilds, 'allow_international_wires':allow_international_wires}
    if request.method == 'POST':
        form = WireForm(request.POST)
        if form.is_valid():
            user                        =  request.user.client
            name                        =  form.cleaned_data['name']
            destination                 =  form.cleaned_data['destination']
            currency                    =  form.cleaned_data['currency']
            sending_account_number      =  form.cleaned_data['sending_account_number']
            sending_account_type        =  form.cleaned_data['sending_account_type']
            sending_amount              =  form.cleaned_data['sending_amount']
            sending_businessname        =  form.cleaned_data['sending_businessname']
            sending_street_address      =  form.cleaned_data['sending_street_address']
            sending_city                =  form.cleaned_data['sending_city']
            sending_state               =  form.cleaned_data['sending_state']
            sending_zipcode             =  form.cleaned_data['sending_zipcode']
            effective_date              =  form.cleaned_data['effective_date']
            recipient_name              =  form.cleaned_data['recipient_name']
            recipient_account_type      =  form.cleaned_data['recipient_account_type']
            recipient_account_number    =  form.cleaned_data['recipient_account_number']
            recipient_routing_number    =  form.cleaned_data['recipient_routing_number']
            recipient_street_address    =  form.cleaned_data['recipient_street_address']
            recipient_city              =  form.cleaned_data['recipient_city']
            recipient_state             =  form.cleaned_data['recipient_state']
            recipient_zipcode           =  form.cleaned_data['recipient_zipcode']
            receiving_bank_name         =  form.cleaned_data['receiving_bank_name']
            receiving_street_address    =  form.cleaned_data['receiving_street_address']
            receiving_bank_city         =  form.cleaned_data['receiving_bank_city']
            receiving_bank_state        =  form.cleaned_data['receiving_bank_state']
            receiving_bank_zipcode      =  form.cleaned_data['receiving_bank_zipcode']
            intermediary_bank_name      =  form.cleaned_data['intermediary_bank_name']
            intermediary_bank_st_adress =  form.cleaned_data['intermediary_bank_st_adress']
            intermediary_bank_country   =  form.cleaned_data['intermediary_bank_country']
            intermediary_bank_state      =  form.cleaned_data['intermediary_bank_state']
            intermediary_bank_country_name   =  form.cleaned_data['intermediary_bank_country_name']
            intermediary_bank_post_code =  form.cleaned_data['intermediary_bank_post_code']
            intermediary_routing_number =  form.cleaned_data['intermediary_routing_number']
            intermediary_bank_swift     =  form.cleaned_data['intermediary_bank_swift']
            intermediary_bank_iban      =  form.cleaned_data['intermediary_bank_iban']
            purpose_of_wire             =  form.cleaned_data['purpose_of_wire']
            description                 =  form.cleaned_data['description']
            template_info = FormTemplate(user=user,name=name,destination=destination,currency=currency,sending_account_number=sending_account_number,sending_account_type=sending_account_type,sending_amount=sending_amount,sending_businessname=sending_businessname,sending_street_address=sending_street_address,sending_city=sending_city,sending_state=sending_state,sending_zipcode=sending_zipcode,effective_date=effective_date,recipient_name=recipient_name,recipient_account_type=recipient_account_type,recipient_account_number=recipient_account_number,recipient_routing_number=recipient_routing_number,recipient_street_address=recipient_street_address,recipient_city=recipient_city,recipient_state=recipient_state,recipient_zipcode=recipient_zipcode,receiving_bank_name=receiving_bank_name,receiving_street_address=receiving_street_address,receiving_bank_city=receiving_bank_city,receiving_bank_state=receiving_bank_state,receiving_bank_zipcode=receiving_bank_zipcode,intermediary_bank_name=intermediary_bank_name,intermediary_bank_st_adress=intermediary_bank_st_adress,intermediary_bank_country=intermediary_bank_country,
            intermediary_bank_state=intermediary_bank_state,intermediary_bank_country_name=intermediary_bank_country_name,
            intermediary_bank_post_code=intermediary_bank_post_code,intermediary_bank_swift=intermediary_bank_swift,intermediary_bank_iban=intermediary_bank_iban,intermediary_routing_number=intermediary_routing_number,purpose_of_wire=purpose_of_wire,description=description     
            )
            template_info.save()
            return redirect('/templates')
        else:
            messages.error(request, 'Form validation failed. Please correct the errors.')
            form.fields['sending_account_number'].queryset = UserAccountNumber.objects.filter(user_id=request.user.id)
            return render(request, 'formTemplates/template.html', {'form': form})
        
        
    return render(request,"formTemplates/template.html",context)

@login_required(login_url='login')  
@client_required
def update_template(request,pk):
    show_element = True
    reccurency_instructions = False
    reccurency_feilds       = False
    template = FormTemplate.objects.filter(id=pk).first()
    form = WireForm(instance=template,user_id=request.user.id)
    allow_international_wires = does_credit_union_allow_international_wires(request)
    if request.method == 'POST':
        form = WireForm(request.POST,instance=template)
        if form.is_valid():
            form.save()
            return redirect('/templates')
        else:
            messages.error(request, 'Form validation failed. Please correct the errors.')
            return render(request, 'formTemplates/template.html', {'form': form, 'allow_international_wires': allow_international_wires})

    elif(template is None or (not request.user.is_staff and request.user.client != template.user)):
        return redirect('/templates')
    else:
        context = {'form':form,'show_element':show_element,'reccurency_instructions':reccurency_instructions,'reccurency_feilds':reccurency_feilds, 'allow_international_wires': allow_international_wires}
        return render(request,"formTemplates/template.html",context)


@login_required(login_url='login')  
@client_required
def delete_template(request, pk):
    template = FormTemplate.objects.get(id=pk)
    if request.method == 'POST':
        template.delete()
        return redirect('/templates')
    context = {'template':template}
    return render(request, 'formTemplates/delete_template.html', context)


class TemplateView(DetailView):
    model = FormTemplate
    fields = '__all__'
    query_pk_and_slug = True
    template_name = "formTemplates/submit_template.html"
    
    def get_context_data(self, **kwargs):
        context = super(TemplateView, self).get_context_data(**kwargs)
        form = WireForm(user_id=self.request.user.id)
        context['form'] = form
        return context
  



@login_required(login_url='login') 
@client_required
def get_reccurent_list(request):
        form = WireFormDetails()
        reccurency = request.user.client.wireformdetails_set.filter(recurrent=True)
        context = {'reccurency': reccurency, 'form': form}
        return render(request, "reccurency/reccurent_list.html", context)


@login_required(login_url='login')  
@client_required
def update_recurrence(request,pk):
    show_element = False
    reccurency_instructions = True
    reccurency_feilds       = True
    template = WireFormDetails.objects.filter(id=pk).first()
    form = WireForm(instance=template,user_id=request.user.id)
    allow_international_wires = does_credit_union_allow_international_wires(request)
    if request.method == 'POST':
        form = WireForm(request.POST,instance=template,user_id=request.user.id)
        if form.is_valid():
            form.save()
            return redirect('/recurrence')
        else:
            print(form.errors)



    if(template is None or not template.recurrent or (not request.user.is_staff and request.user.client != template.user)):
        return redirect('/recurrence')
    else:
        context = {'form':form,'show_element':show_element,'reccurency_instructions':reccurency_instructions,'reccurency_feilds':reccurency_feilds, 'allow_international_wires': allow_international_wires}
        return render(request,"formTemplates/template.html",context)


@login_required(login_url='login') 
@client_required
def delete_recurrence(request, pk):
    template = WireFormDetails.objects.get(id=pk)
    if request.method == 'POST':
        template.delete()
        return redirect('/templates')
    context = {'template':template}
    return render(request, 'formTemplates/delete_template.html', context)
     


@login_required(login_url='login')
@staff_only
def dashboard(request):
    today = datetime.now().date()
    order = Order.objects.exclude(status="Approved").order_by('-date_created')
    recurrent_orders_count =ReccurentOrder.objects.count()
    todays_orders_count = Order.objects.filter(date_created__date=today).count()
    pending_orders_count = Order.objects.filter(status='Pending').count()
    processing_orders_count = Order.objects.filter(status='Processing').count()
    completed_orders_count = Order.objects.filter(status='Approved').count()
    form = WireFormDetails()
    # Construct the context dictionary to pass to the template
    context = {
        'recurrent_orders_count': recurrent_orders_count,
        'todays_orders_count': todays_orders_count,
        'pending_orders_count': pending_orders_count,
        'processing_orders_count': processing_orders_count,
        'completed_orders_count': completed_orders_count,
        'order':order,
        'form':form
    }
    if request.user.is_staff and not request.user.staff.is_approved:
        return render(request, 'accounts/account_pending.html',context) 
    

    # Render the template with the context data
    return render(request, 'dashboard/dashboard.html',context) 

class RecurrentOrderListView(ListView):
    model = Order
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(wire_details__recurrent=True).order_by('-date_created')

class PendingOrderListView(ListView):
    model = Order
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(status='Pending').order_by('-date_created')

class ProccesingOrderListView(ListView):
    model = Order
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'order'
    
    def get_queryset(self):
        return Order.objects.filter(status='Processing').order_by('-date_created')

class CompletedOrderListView(ListView):
    model = Order
    template_name = 'dashboard/dashboard.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(status='Approved').order_by('-date_created')


@login_required(login_url='login') 
@staff_only
def update_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    wire_form = WireForm(instance=order.wire_details,user_id=order.wire_details.user_id)
    order_form = OrderForm(instance=order)
    order.wire_details.sending_state = get_full_state_by_abbreviation(order.wire_details.sending_state)
    order.wire_details.recipient_state = get_full_state_by_abbreviation(order.wire_details.recipient_state)
    order.wire_details.receiving_bank_state = get_full_state_by_abbreviation(order.wire_details.receiving_bank_state)
    order.wire_details.intermediary_bank_state = get_full_state_by_abbreviation(order.wire_details.intermediary_bank_state)
    order.wire_details.intermediary_bank_country = get_full_country_by_abbreviation(order.wire_details.intermediary_bank_country) 
    if request.method == 'POST':
        wire_form = WireForm(request.POST, instance=order.wire_details,user_id=order.wire_details.user_id)
        order_form = OrderForm(request.POST, instance=order)
        if order_form.is_valid():
            #wire_form.save()
            order_form.save()
            return redirect('/dashboard')
    allow_international_wires = does_credit_union_allow_international_wires(request)
    context = {
        'wire_form': wire_form,
        'order_form': order_form,
        'order': order,
        'allow_international_wires': allow_international_wires
    }
    return render(request,"dashboard/orders_detail.html",context)

@login_required(login_url='login')
@staff_only
def delete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('/dashboard')
    context = {'order':order}
    return render(request, 'dashboard/delete_order.html', context)


def custom_404_page(request, exception):
    return render(request, '404.html', status=404)


def get_full_state_by_abbreviation(abbreviation):
    state_dict = dict(STATES_NULL)
    if abbreviation in state_dict:
        return state_dict[abbreviation]
    else:
        return abbreviation
    
def get_full_country_by_abbreviation(abbreviation):
    country_dict = dict(COUNTRY)
    if abbreviation in country_dict:
        return country_dict[abbreviation]
    else:
        return abbreviation
    
def notify_users_of_wire_submission(request, order):
    authorizer = WireAuthorizationPair.objects.filter(sub_user_id=request.user.client.id).first()
    # wire does not need to be authorized
    if(authorizer is None):                
        send_order_confirmation_email(request, order)
    else:
        WireAuthorization.objects.create(wire_details=order, authorization_pair=authorizer,authorized=None)
        send_wire_authorization_email(request, order, authorizer)

def send_order_confirmation_email(request, wire_details):
    subject = 'A wire request has been submitted'
    subject2 = 'Your wire request has been submitted'
    from_email = settings.EMAIL_HOST_USER
    tenant_model = get_tenant_model()
    tenant = tenant_model.objects.get(schema_name=request.tenant.schema_name)
    domain_model = get_domain_model()
    domain = domain_model.objects.get(tenant_id=tenant.id)
    if not tenant:
        to_email   = settings.EMAIL_HOST_USER
    else:
        to_email = tenant.email
        
    recieving_email   = request.user.client.email
    
    if not domain:
        domain_url = 'https://truwires.com/dashboard/'
    else:
        domain_url = 'https://' + domain.domain + "/dashboard/"
        


    template = get_template('management/wire_submission_notification.html')
    template2 = 'management/wire_confirmation.html'
    context  = {'user': wire_details.user, 'sending_amount':wire_details.sending_amount, 'recipient_name':wire_details.recipient_name,'effective_date':wire_details.effective_date, 'destination':wire_details.destination, 'domain_url': domain_url}
    content = template.render(context)
    content2 = render_to_string(template2,context)

    email= EmailMessage(
            subject,
            content,
            from_email,
            [to_email],
            )
    email2= EmailMessage(
            subject2,
            content2,
            from_email,
            [recieving_email],
            )
    email.content_subtype =  'html'
    email2.content_subtype = 'html'
    try:
        email.send(fail_silently=False)
        email2.send(fail_silently=False)
    except BadHeaderError:
            return HttpResponse('Invalid Header found.')
    except SMTPException:
            return HttpResponse("Email Error occured")
    
def send_wire_authorization_email(request, order, authorizer):
    subject = 'A wire request has been submitted for authorization'
    subject2 = 'Your wire request has been submitted for authorization'
    from_email = settings.EMAIL_HOST_USER
    tenant_model = get_tenant_model()
    tenant = tenant_model.objects.get(schema_name=request.tenant.schema_name)
    domain_model = get_domain_model()
    domain = domain_model.objects.get(tenant_id=tenant.id)

    if not authorizer:
        if not tenant:
            to_email   = settings.EMAIL_HOST_USER
        else:
            to_email = tenant.email
    else:
        to_email = authorizer.authorizer.email
        
    recieving_email   = request.user.client.email
    
    if not domain:
        domain_url = 'https://truwires.com/authorization/'
    else:
        domain_url = 'https://' + domain.domain + "/authorization/"
        


    template = get_template('management/wire_authorization_notifcation.html')
    template2 = 'management/wire_authorization.html'
    context  = {'user': order.user, 'sending_amount':order.sending_amount, 'recipient_name':order.recipient_name,'effective_date':order.effective_date, 'destination':order.destination, 'domain_url': domain_url}
    content = template.render(context)
    content2 = render_to_string(template2,context)

    email= EmailMessage(
            subject,
            content,
            from_email,
            [to_email],
            )
    email2= EmailMessage(
            subject2,
            content2,
            from_email,
            [recieving_email],
            )
    email.content_subtype =  'html'
    email2.content_subtype = 'html'
    try:
        email.send(fail_silently=False)
        email2.send(fail_silently=False)
    except BadHeaderError:
            return HttpResponse('Invalid Header found.')
    except SMTPException:
            return HttpResponse("Email Error occured")
    
def is_user_authorizer(user_id):
    authorizer = WireAuthorizationPair.objects.filter(authorizer=user_id)
    
    if(authorizer.count() > 0):
        return True
    else:
        return False
    
def is_user_sub_user(client_id):
    sub_user = WireAuthorizationPair.objects.filter(sub_user=client_id)
    if(sub_user.count() > 0):
        return True
    else:
        return False
    
def does_credit_union_allow_international_wires(request):
    tenant_model = get_tenant_model()
    tenant = tenant_model.objects.get(schema_name=request.tenant.schema_name)
    return tenant.allow_international_wires