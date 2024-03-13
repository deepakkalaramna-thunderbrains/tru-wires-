from tenant_schemas.routers import TenantMixin
from django.db import connection
from django.conf import settings

class TenantRouter(TenantMixin):
    def _get_tenant_domain(self, tenant):
        return tenant.domain_url

    def _get_schema_name(self, domain_url):
        """
        This function should return schema name for a given request.
        """
        # Get the tenant associated with the request domain URL
        tenant = Tenant.objects.get(domain_url=domain_url)
        # Return the schema name associated with the tenant
        return tenant.schema_name

    def db_for_read(self, model, **hints):
        domain_url = connection.tenant.domain_url if connection.tenant else getattr(settings, 'PUBLIC_SCHEMA_URL', None)
        schema_name = self._get_schema_name(domain_url)
        return schema_name

    def db_for_write(self, model, **hints):
        domain_url = connection.tenant.domain_url if connection.tenant else getattr(settings, 'PUBLIC_SCHEMA_URL', None)
        schema_name = self._get_schema_name(domain_url)
        return schema_name

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'default':
            return app_label == 'auth'
        return True