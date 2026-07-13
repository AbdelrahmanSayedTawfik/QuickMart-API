from rest_framework import generics
from apps.warehouses.permissions import IsAdminOrReadOnly 
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.warehouses.services.city_service import WarehouseCityService


class AvailableCitiesView(generics.GenericAPIView):
    permission_classes = [IsAdminOrReadOnly]

    @extend_schema(
        tags=['Warehouse'],
        summary='List available shipping cities',
        description='Returns cities currently served by at least one active warehouse. Used to populate city dropdowns at registration/checkout — never hardcode this list on the frontend.',
        responses={200: OpenApiResponse(description='List of city names')}
    )
    def get(self, request):
        return Response({'cities': WarehouseCityService.get_available_cities()})