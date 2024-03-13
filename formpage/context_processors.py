from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django_pgschemas.utils import get_tenant_model


def tenant_context(request):
    try:
        tenant_model = get_tenant_model()
        tenant = tenant_model.objects.get(schema_name=request.tenant.schema_name)
        cunion = tenant
        return {'cunion': cunion if cunion else None}
    except ObjectDoesNotExist:
        default_tenant = settings.TENANTS.get('public')
        if default_tenant and default_tenant.get('DOMAIN_URL') and request.get_host().startswith(default_tenant.get('DOMAIN_URL')):
            default_store_model = default_tenant.get('STORE_MODEL')
            default_store = default_store_model.objects.first()
            if default_store and default_store.logo:
                return {'logo': default_store.logo.url}
        return {'logo': None}





    # try:
    #     tenant_model = get_tenant_model()
    #     tenant = tenant_model.objects.get(schema_name=request.tenant.schema_name)
    #     cunion = tenant
    # except tenant_model.DoesNotExist:
    #     cunion = objects.get(name='My Store')
    # print("the Cunion is ", cunion)
    # # logo = get_logo()
    # # print("the logo is ", logo)