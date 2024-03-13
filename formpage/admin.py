from django.contrib import admin
from .models import Client,FormTemplate,Order, ReccurentOrder,Staff ,WireFormDetails, UserAccountNumber, WireAuthorizationPair, WireAuthorization, WireUserAmountLimit

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
