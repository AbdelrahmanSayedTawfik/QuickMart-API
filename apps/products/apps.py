from django.apps import AppConfig


class ProductsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    label = 'products'
    
    def ready(self):
        import apps.products.signals.signals
        from apps.products.services.csv_import import CSVImportService
        from apps.products.management.commands.importers.category import CategoryImporter
        from apps.products.management.commands.importers.product import ProductImporter

        
        CSVImportService.register_importer('categories', CategoryImporter)
        CSVImportService.register_importer('products', ProductImporter)

