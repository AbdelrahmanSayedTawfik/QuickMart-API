from apps.warehouses.models.warehouse import Warehouse

class WarehouseCityService:
    
    @staticmethod
    def get_available_cities() -> list[str]:
        """
        Single source of truth for which cities are currently served.
        Always reads live from the Warehouse table — never hardcoded.
        """
        return list(
            Warehouse.objects.filter(is_active = True)
            .exclude(city__isnull=True)
            .exclude(city__exact='')
            .values_list('city',flat=True)
            .distinct()
            .order_by('city')
        )
        