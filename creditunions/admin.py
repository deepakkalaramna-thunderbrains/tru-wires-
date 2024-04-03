from django.contrib import admin
from .models import CreditUnion, Domain
# Register your models here.

class CreditUnionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
            #Schema must be lower case on initial creation
            if(obj.id is None):
                obj.schema_name = obj.schema_name.lower()
            super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = super().get_queryset(request)
            return queryset
        queryset = super().get_queryset(request)
        current_domain_with_port = request.META.get('HTTP_HOST', '')
        current_domain = current_domain_with_port.split('.')[0]  

        queryset = queryset.filter(schema_name=current_domain)
        return queryset
    
class DomainAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        if request.user.is_superuser:
            queryset = super().get_queryset(request)
            return queryset 
        queryset = super().get_queryset(request)
        current_domain_with_port = request.META.get('HTTP_HOST', '')
        current_domain = current_domain_with_port.split(':')[0]  
        queryset = queryset.filter(domain=current_domain)
        return queryset

admin.site.register(CreditUnion, CreditUnionAdmin)
admin.site.register(Domain, DomainAdmin)