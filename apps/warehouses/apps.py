from django.apps import AppConfig


class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.warehouses'
    
    def ready(self):
        import apps.warehouses.signals.signals 
