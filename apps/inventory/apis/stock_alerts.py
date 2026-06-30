from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from apps.inventory.models.stock_alert import StockAlert
from apps.inventory.serializers.stock_alert import StockAlertSerializer, ResolveAlertSerializer
from apps.inventory.services.alert import AlertService
from apps.products.permissions import IsAdminOrSeller


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory'],
        summary='List stock alerts',
        description='Get all stock alerts. Unresolved shown first.',
    )
)
class StockAlertListView(generics.ListAPIView):

    serializer_class = StockAlertSerializer
    permission_classes = [IsAdminOrSeller]

    def get_queryset(self):
        qs = StockAlert.objects.with_product()  # already does select_related('product', 'resolved_by')

        alert_type = self.request.query_params.get('type')
        if alert_type:
            qs = qs.filter(alert_type=alert_type)

        status_filter = self.request.query_params.get('status')
        if status_filter == 'unresolved':
            qs = qs.unresolved()
        elif status_filter == 'resolved':
            qs = qs.resolved()


        return qs


@extend_schema_view(
    get=extend_schema(tags=['Inventory'], summary='Get alert details'),
    post=extend_schema(
        tags=['Inventory'],
        summary='Resolve alert',
        description='Mark alert as resolved with optional notes.',
        request=ResolveAlertSerializer,
        responses={
            200: OpenApiResponse(description='Alert resolved'),
            400: OpenApiResponse(description='Already resolved'),
        }
    )
)
class StockAlertDetailView(generics.RetrieveAPIView):

    # FIX: was StockAlert.objects.all() — no joins, causing N+1 on product + resolved_by
    queryset = StockAlert.objects.with_product()
    serializer_class = StockAlertSerializer
    permission_classes = [IsAdminOrSeller]

    def post(self, request, pk):
        alert = self.get_object()

        if alert.is_resolved:
            return Response(
                {'error': 'Alert already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ResolveAlertSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        AlertService.resolve_alert(
            alert_id=alert.id,
            user=request.user,
            note=serializer.validated_data.get('resolution_note', '')
        )

        return Response(
            {'message': 'Alert resolved successfully'},
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Inventory'],
        summary='Alert summary',
        description='Quick stats for dashboard.',
    )
)
class AlertSummaryView(generics.GenericAPIView):

    permission_classes = [IsAdminOrSeller]

    def get(self, request):
        summary = AlertService.get_alert_summary()
        return Response(summary)