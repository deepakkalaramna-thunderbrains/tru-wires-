from django.contrib import admin
from .models import Client,FormTemplate,Order, ReccurentOrder,Staff ,WireFormDetails, UserAccountNumber, WireAuthorizationPair, WireAuthorization, WireUserAmountLimit
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


# db models registerd here
admin.site.register(Client)
admin.site.register(FormTemplate)
admin.site.register(Order)
admin.site.register(ReccurentOrder)
admin.site.register(Staff)
admin.site.register(WireFormDetails)
admin.site.register(UserAccountNumber)
admin.site.register(WireAuthorizationPair)
admin.site.register(WireAuthorization)
admin.site.register(WireUserAmountLimit)


class CustomUserAdmin(UserAdmin):
    def get_queryset(self, request):
        # Get the base queryset
        queryset = super().get_queryset(request)
        # Filter queryset based on whether the user is staff or not
        if request.user.is_staff and not request.user.is_superuser:
            return queryset.filter(id=request.user.id)
        else:
            return queryset
        
admin.site.unregister(User)

# Register the CustomUserAdmin
admin.site.register(User, CustomUserAdmin)