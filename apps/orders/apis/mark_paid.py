from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
from django.core.exceptions import ValidationError
from apps.orders.models.order import Order
from apps.orders.serializers.order import OrderSerializer
from apps.orders.services.mark_paid import MarkOrderPaidService


@extend_schema_view(
    post=extend_schema(
        tags=['Orders'],
        summary='Mark order as paid (Local Testing)',
        description='''
        **Simulates a successful payment for local development.**
        
        Since Stripe webhooks don't work locally, use this endpoint to test the full post-payment flow:
        
        1. ✅ Validates order is `pending`
        2. ✅ Marks order as `paid` with timestamp
        3. ✅ **Deducts stock** from each product
        4. ✅ Creates `stock_movements` records (`type='out'`)
        5. ✅ Creates `payment` record
        6. ✅ Logs status change in `order_status_logs`
        7. ✅ Triggers low-stock alerts if needed
        
        **Atomic transaction** — if anything fails, nothing is saved.
        
        **Permissions:** Only the order owner (or admin) can call this.
        **Restrictions:** Only `pending` orders can be marked paid.
        
        ⚠️ **Do NOT expose in production** — replace with real Stripe webhook handler.
        ''',
        request=None,
        responses={
            200: OpenApiResponse(
                response=OrderSerializer,
                description='Order marked as paid. Stock deducted, payment recorded.'
            ),
            400: OpenApiResponse(
                description='Order already paid, cancelled, or invalid status transition'
            ),
            403: OpenApiResponse(
                description='Not the order owner'
            ),
            404: OpenApiResponse(
                description='Order not found'
            ),
        },
        examples=[
            OpenApiExample(
                'Mark as Paid',
                summary='Simple call, no body needed',
                value={},
                request_only=True,
            ),
        ]
    )
)
class MarkOrderPaidView(generics.GenericAPIView):
    """
    POST /api/orders/{number}/mark-paid/
    
    Simulates payment success for local testing.
    Mirrors production webhook flow exactly.
    """
    permission_classes = [IsAuthenticated]
    lookup_field = 'order_number'
    queryset = Order.objects.all()

    def get_queryset(self):
        """Users see their own orders. Admins see all."""
        user = self.request.user
        if user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user=user)

    def post(self, request, order_number, *args, **kwargs):
        # Get order (404 if not found or not owned)
        order = get_object_or_404(self.get_queryset(), order_number=order_number)

        try:
            # Process via service (atomic transaction)
            order = MarkOrderPaidService.process(
                user=request.user,
                order=order
            )
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {
                'message': 'Order marked as paid successfully.',
                'order': OrderSerializer(order).data
            },
            status=status.HTTP_200_OK
        )