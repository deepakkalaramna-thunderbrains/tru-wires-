from django.apps import AppConfig


class FormpageConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'formpage'
    
    def ready(self):
        import formpage.signals

from django.dispatch import Signal

post_schema_sync = Signal()