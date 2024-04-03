from django.db import models
from django_pgschemas.models import TenantMixin, DomainMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django_pgschemas.schema import SchemaDescriptor
from django.contrib.contenttypes.models import ContentType
from django.db import connection



User = get_user_model()

class CreditUnion(TenantMixin):
    name         = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20,default="321 092 2093")
    email        = models.EmailField(max_length=50, default="support@support.com")
    logo         = models.ImageField(upload_to='images',null=True)
    header_color = models.CharField(max_length=20, default='#F9F4F4')
    form_color = models.CharField(max_length=20, default='rgb(114, 143, 206)')
    footer_color = models.CharField(max_length=20, default='rgb(245, 222, 179)')
    buttons_color = models.CharField(max_length=20, default='#027FAA')
    created_on = models.DateField(auto_now_add=True)
    allow_international_wires = models.BooleanField(null=False, default=True)
    
    def __str__(self):
        return  '%s'%(self.name)

class Domain(DomainMixin):
    domain = models.CharField(max_length=100)

    def __str__(self):
        return  '%s'%(self.domain)
    
    def save(self, *args, **kwargs):
        user, created = User.objects.get_or_create(username=self.tenant.name)
        if created:
            user.set_password("Testword1!")
            user.is_staff = True
            user.is_superuser = False
            user.save()
            content_type = ContentType.objects.get_for_model(User)
            permission = Permission.objects.all()
            user.user_permissions.set(permission)
        with SchemaDescriptor.create(schema_name=self.tenant.schema_name):
            user, created = User.objects.get_or_create(username=self.tenant.name)
            if created:
                user.set_password("Testword1!")
                user.is_staff = True
                user.is_superuser = False
                user.save()
                content_type = ContentType.objects.get_for_model(User)
                permission = Permission.objects.all()
                user.user_permissions.set(permission)
        super(Domain, self).save(*args, **kwargs)
