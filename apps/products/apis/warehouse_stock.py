from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import (
    extend_schema_view, extend_schema, OpenApiResponse,
    OpenApiParameter, OpenApiExample
)

from apps.products.models.product import Product
from apps.products.models.warehouse import Warehouse
from apps.products.models.warehouse_stock import WarehouseStock
from apps.products.serializers.warehouse_stock import (
    StockSerializer, InOutSerializer, TransferSerializer, AdjustSerializer
)
from apps.products.services.warehouse_stock_service import StockService, StockError
from apps.products.permissions import IsWarehouseManagerOrAdmin


class WarehouseMixin:

    permission_classes = (IsWarehouseManagerOrAdmin,)

    def get_warehouse(self, warehouse_id):
        try:
            return Warehouse.objects.get(id=warehouse_id, is_active=True)
        except Warehouse.DoesNotExist:
            raise NotFound('Warehouse not found or inactive.')

@extend_schema_view(
    get=extend_schema(
        tags=['Warehouse Stock'],
        summary='Summarize product stock',
        description='Get total stock and breakdown across all warehouses for a product.',
        parameters=[
            OpenApiParameter(
                name='product_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Product ID to summarize'
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Stock summary',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'total': 170,
                            'warehouses': [
                                {
                                    'name': 'Cairo Main',
                                    'code': 'CAI',
                                    'city': 'Cairo',
                                    'qty': 150,
                                    'transfer_in': 50,
                                    'transfer_out': 30,
                                    'is_low': False,
                                    'is_empty': False,
                                    'threshold': 5
                                },
                                {
                                    'name': 'Alexandria',
                                    'code': 'ALY',
                                    'city': 'Alexandria',
                                    'qty': 20,
                                    'transfer_in': 30,
                                    'transfer_out': 0,
                                    'is_low': True,
                                    'is_empty': False,
                                    'threshold': 5
                                }
                            ]
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden'),
        }
    )
)
class ProductStockSummaryView(WarehouseMixin, generics.GenericAPIView):
    def get(self, request, product_id):
        return Response(StockService.summarize(product_id))

@extend_schema_view(
    get=extend_schema(
        tags=['Warehouse Stock'],
        summary='List warehouse stock',
        description='Get all stock records for a specific warehouse.',
        parameters=[
            OpenApiParameter(
                name='warehouse_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Warehouse ID'
            ),
        ],
        responses={
            200: OpenApiResponse(
                response=StockSerializer,
                description='Paginated list of stock records',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'count': 50,
                            'results': [
                                {
                                    'id': 10,
                                    'warehouse': {'id': 1, 'name': 'Cairo Main'},
                                    'product_name': 'iPhone 15',
                                    'product_sku': 'IPH-15-128',
                                    'quantity': 150,
                                    'transfer_in': 50,
                                    'transfer_out': 30,
                                    'low_stock_threshold': 5,
                                    'is_low': False,
                                    'is_empty': False,
                                    'updated_at': '2024-07-07T10:00:00Z'
                                }
                            ]
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden'),
            404: OpenApiResponse(description='Warehouse not found'),
        }
    )
)
class WarehouseStockListView(WarehouseMixin, generics.ListAPIView):
    serializer_class = StockSerializer

    def get_queryset(self):
        return WarehouseStock.objects.filter(
            Warehouse_id=self.kwargs.get('warehouse_id')
        ).select_related('Warehouse', 'Product')

@extend_schema_view(
    post=extend_schema(
        tags=['Warehouse Stock'],
        summary='Receive stock',
        description='Add inventory to warehouse. Creates audit trail.',
        parameters=[
            OpenApiParameter(
                name='warehouse_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Warehouse ID to receive stock into'
            ),
        ],
        request=InOutSerializer,
        responses={
            201: OpenApiResponse(
                response=StockSerializer,
                description='Stock received successfully',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'id': 10,
                            'warehouse': {'id': 1, 'name': 'Cairo Main'},
                            'product_name': 'iPhone 15',
                            'product_sku': 'IPH-15-128',
                            'quantity': 250,
                            'transfer_in': 50,
                            'transfer_out': 30,
                            'low_stock_threshold': 5,
                            'is_low': False,
                            'is_empty': False,
                            'updated_at': '2024-07-07T10:00:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Invalid data',
                examples=[
                    OpenApiExample(
                        'Invalid quantity',
                        value={'qty': ['Ensure this value is greater than or equal to 1.']}
                    ),
                    OpenApiExample(
                        'Product not found',
                        value={'product_id': ['Product not found.']}
                    )
                ]
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - not your warehouse'),
            404: OpenApiResponse(description='Warehouse not found'),
        }
    )
)
class StockInView(WarehouseMixin, generics.GenericAPIView):
    serializer_class = InOutSerializer

    def post(self, request, warehouse_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = self.get_warehouse(warehouse_id)
        product = Product.objects.get(id=data['product_id'])

        stock = StockService.add_stock_external_src(
            warehouse=warehouse, 
            product=product, 
            qty=data['qty'],
            ref=data['ref'], 
            note=data['note'], 
            user=request.user
        )
        return Response(StockSerializer(stock).data, status=status.HTTP_201_CREATED)

@extend_schema_view(
    post=extend_schema(
        tags=['Warehouse Stock'],
        summary='Dispatch stock',
        description='Remove inventory from warehouse. Creates audit trail.',
        parameters=[
            OpenApiParameter(
                name='warehouse_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Warehouse ID to dispatch stock from'
            ),
        ],
        request=InOutSerializer,
        responses={
            200: OpenApiResponse(
                response=StockSerializer,
                description='Stock dispatched successfully',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'id': 10,
                            'warehouse': {'id': 1, 'name': 'Cairo Main'},
                            'product_name': 'iPhone 15',
                            'quantity': 140,
                            'transfer_in': 50,
                            'transfer_out': 30,
                            'is_low': False,
                            'is_empty': False,
                            'updated_at': '2024-07-07T10:00:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Insufficient stock or invalid data',
                examples=[
                    OpenApiExample(
                        'Insufficient stock',
                        value={'error': 'Not enough at Cairo Main. Have: 5, Need: 10'}
                    )
                ]
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - not your warehouse'),
            404: OpenApiResponse(description='Warehouse or product not found'),
        }
    )
)
class StockOutView(WarehouseMixin, generics.GenericAPIView):
    serializer_class = InOutSerializer

    def post(self, request, warehouse_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = self.get_warehouse(warehouse_id)
        product = Product.objects.get(id=data['product_id'])

        try:
            stock = StockService.remove_stock_external_src(
                warehouse=warehouse, 
                product=product, 
                qty=data['qty'],
                ref=data['ref'], 
                note=data['note'], 
                user=request.user
            )
        except StockError as error:
            return Response({'error': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(StockSerializer(stock).data)

@extend_schema_view(
    post=extend_schema(
        tags=['Warehouse Stock'],
        summary='Transfer stock',
        description='Move stock from this warehouse to another warehouse. Creates two audit records.',
        parameters=[
            OpenApiParameter(
                name='warehouse_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Source warehouse ID'
            ),
        ],
        request=TransferSerializer,
        responses={
            200: OpenApiResponse(
                description='Transfer completed',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'message': 'Transfer complete',
                            'source': {
                                'id': 10,
                                'warehouse': {'id': 1, 'name': 'Cairo Main'},
                                'quantity': 70,
                                'transfer_in': 50,
                                'transfer_out': 60,
                                'is_low': False
                            },
                            'destination': {
                                'id': 11,
                                'warehouse': {'id': 2, 'name': 'Alexandria'},
                                'quantity': 80,
                                'transfer_in': 60,
                                'transfer_out': 0,
                                'is_low': False
                            }
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Insufficient stock or same warehouse',
                examples=[
                    OpenApiExample(
                        'Insufficient stock',
                        value={'error': 'Not enough at Cairo Main. Have: 5, Need: 30'}
                    ),
                    OpenApiExample(
                        'Same warehouse',
                        value={'error': 'Cannot transfer to same warehouse.'}
                    )
                ]
            ),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - not your warehouse'),
            404: OpenApiResponse(description='Warehouse or product not found'),
        }
    )
)
class StockTransferView(WarehouseMixin, generics.GenericAPIView):
    serializer_class = TransferSerializer

    def post(self, request, warehouse_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        source = self.get_warehouse(warehouse_id)
        destination = Warehouse.objects.get(id=data['dest_wh_id'], is_active=True)
        product = Product.objects.get(id=data['product_id'])

        if source.id == destination.id:
            return Response({'error': 'Cannot transfer to same warehouse.'}, status=400)

        try:
            source_stock, destination_stock = StockService.transfer_warehouses(
                source=source, 
                destination=destination, 
                product=product, 
                qty=data['qty'],
                ref=data['ref'], 
                note=data['note'], 
                user=request.user
            )
        except StockError as error:
            return Response({'error': str(error)}, status=400)

        return Response({
            'message': 'Transfer complete',
            'source': StockSerializer(source_stock).data,
            'destination': StockSerializer(destination_stock).data,
        })

@extend_schema_view(
    post=extend_schema(
        tags=['Warehouse Stock'],
        summary='Adjust stock',
        description='Manually set stock quantity. Creates audit trail.',
        parameters=[
            OpenApiParameter(
                name='warehouse_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Warehouse ID'
            ),
            OpenApiParameter(
                name='product_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Product ID to adjust'
            ),
        ],
        request=AdjustSerializer,
        responses={
            200: OpenApiResponse(
                response=StockSerializer,
                description='Stock adjusted',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'id': 10,
                            'warehouse': {'id': 1, 'name': 'Cairo Main'},
                            'product_name': 'iPhone 15',
                            'quantity': 95,
                            'is_low': False,
                            'updated_at': '2024-07-07T10:00:00Z'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(description='Invalid data'),
            401: OpenApiResponse(description='Unauthorized'),
            403: OpenApiResponse(description='Forbidden - not your warehouse'),
            404: OpenApiResponse(description='Warehouse or product not found'),
        }
    )
)
class StockAdjustmentView(WarehouseMixin, generics.GenericAPIView):
    serializer_class = AdjustSerializer

    def post(self, request, warehouse_id, product_id):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        warehouse = self.get_warehouse(warehouse_id)
        product = Product.objects.get(id=product_id)

        stock = StockService.adjust(
            warehouse=warehouse, 
            product=product, 
            new_qty=data['qty'],
            reason=data['reason'], 
            user=request.user
        )
        return Response(StockSerializer(stock).data)

@extend_schema_view(
    get=extend_schema(
        tags=['Shipping'],
        summary='Check shipping availability',
        description='Check if product can be shipped to a city. No authentication required.',
        parameters=[
            OpenApiParameter(
                name='product_id',
                type=int,
                location=OpenApiParameter.PATH,
                description='Product ID'
            ),
            OpenApiParameter(
                name='city',
                type=str,
                location=OpenApiParameter.QUERY,
                description='City name (e.g., Cairo)',
                required=False
            ),
        ],
        responses={
            200: OpenApiResponse(
                description='Shipping eligibility result',
                examples=[
                    OpenApiExample(
                        'Available',
                        value={
                            'can_ship': True,
                            'warehouses': [
                                {
                                    'id': 1,
                                    'name': 'Cairo Main',
                                    'city': 'Cairo',
                                    'qty': 150,
                                    'is_low': False
                                }
                            ]
                        }
                    ),
                    OpenApiExample(
                        'Not available',
                        value={
                            'can_ship': False,
                            'reason': 'Not available in Cairo',
                            'other_cities': ['Alexandria', 'Giza'],
                            'warehouses': []
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='City not provided',
                examples=[
                    OpenApiExample(
                        'Missing city',
                        value={'error': 'Provide ?city=YourCity'}
                    )
                ]
            ),
            404: OpenApiResponse(description='Product not found'),
        }
    )
)
class ShipCheckView(generics.GenericAPIView):
    permission_classes = ()

    def get(self, request, product_id):
        city = request.query_params.get('city') or getattr(request.user, 'city', None)
        if not city:
            return Response({'error': 'Provide ?city=YourCity'}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found.'}, status=404)

        return Response(StockService.check_ship(product, city))