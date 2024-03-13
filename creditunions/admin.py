from django.contrib import admin
from .models import CreditUnion, Domain
# Register your models here.

class CreditUnionAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
            #Schema must be lower case on initial creation
            if(obj.id is None):
                obj.schema_name = obj.schema_name.lower()
            super().save_model(request, obj, form, change)

    

admin.site.register(CreditUnion, CreditUnionAdmin)
admin.site.register(Domain)