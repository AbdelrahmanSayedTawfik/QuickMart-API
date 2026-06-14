from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'
    
    def ready(self):
        """
        Import signals when app starts.
        This connects the post_save signal to Product model.
        """
        import apps.inventory.signals.stock  # noqa