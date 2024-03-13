import re
from django.db import connection
from django.shortcuts import redirect
from django.conf import settings

from django.http import Http404
from creditunions.models import CreditUnion,Domain
from django_pgschemas.utils import get_tenant_model


class StoreSchemaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract subdomain from request
        subdomain = self.extract_subdomain(request)

        # Set schema for the current connection
        connection.set_schema(subdomain)

        response = self.get_response(request)

        return response

    def extract_subdomain(self, request):
        host = request.META.get('HTTP_HOST', '')
        subdomain = re.sub(r'\..*$', '', host)
        return subdomain
    

class TenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # get the subdomain from the request host
        subdomain = request.get_host().split('.')[0]

        # fetch the corresponding store object from the database
        try:
            cunion = Domain.objects.get(domain__contains=subdomain)
            print("calue of cunion",cunion)
        except Domain.DoesNotExist:
            raise Http404

        # add the store object to the request
        request.cunion = cunion

        response = self.get_response(request)

        return response

    def process_template_response(self, request, response):
        # add the store object to the template context
        if hasattr(request, 'cunion'):
            response.context_data['cunion'] = request.cunion

        return response

# class TenantMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         host = request.get_host().lower()
#         subdomain = host.split(".")[0]

#         TenantModel = get_tenant_model()
#         print("my Tenant Model is ", TenantModel)
#         try:
#             cunion = TenantModel.objects.get(domains__domain=subdomain)
#             print("Now cunion is ",cunion)
#             request.cunion = cunion
#         except TenantModel.DoesNotExist:
#             request.cunion = None

#         response = self.get_response(request)
#         return response