from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from apps.products.permissions import IsSellerOrAdminOrReadOnly
from apps.products.services.bulk_update import BulkStockService


@extend_schema(
    tags=['Products'],
    summary='Bulk update stock',
    description='Atomic bulk stock update. All succeed or all fail. Prevents race conditions with row-level locking.',
    request={'type': 'object', 'properties': {
        'updates': {'type': 'array', 'items': {'type': 'object', 'properties': {
            'product_id': {'type': 'integer'},
            'stock_quantity': {'type': 'integer'}
        }}}
    }},
    responses={
        200: OpenApiResponse(description='Stock updated successfully'),
        400: OpenApiResponse(description='Validation error'),
    }
)
@api_view(['POST'])
@permission_classes([IsSellerOrAdminOrReadOnly])
def bulk_update_stock(request):

    updates = request.data.get('updates', [])
    result = BulkStockService.update_stock(updates, user=request.user)
    return Response(result)