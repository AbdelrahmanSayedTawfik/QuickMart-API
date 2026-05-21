# apps/payments/tests/test_payments.py — COMPLETE FIXED VERSION

import pytest
from unittest.mock import patch, MagicMock
from rest_framework import status
from apps.payments.models import Payment


@pytest.mark.django_db
class TestPaymentIntent:
    """Tests for payment intent creation with mocked Stripe."""

    @patch('apps.payments.views.stripe.PaymentIntent.create')
    def test_create_payment_intent_success(self, mock_stripe, auth_client, order):
        """
        Test: Create payment intent returns client_secret.
        @patch mocks stripe so we never call real Stripe API.
        """
        # Configure mock to return fake Stripe response
        mock_stripe.return_value = MagicMock(
            id='pi_test_123',
            client_secret='pi_test_123_secret_xyz',
            status='requires_payment_method'
        )

        response = auth_client.post('/api/payments/create-intent/', {
            'order_number': order.order_number
        }, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert 'client_secret' in response.data
        assert response.data['client_secret'] == 'pi_test_123_secret_xyz'
        assert 'publishable_key' in response.data

        # Verify Stripe was called once
        mock_stripe.assert_called_once()

        # Verify Payment record was created in DB
        assert Payment.objects.filter(order=order).exists()
        payment = Payment.objects.get(order=order)
        assert payment.status == 'pending'
        assert payment.stripe_payment_intent_id == 'pi_test_123'

    @patch('apps.payments.views.stripe.PaymentIntent.create')
    def test_create_payment_intent_already_paid(self, mock_stripe, auth_client, order):
        """Test: Cannot create intent for already paid order."""
        order.status = 'paid'
        order.save()

        response = auth_client.post('/api/payments/create-intent/', {
            'order_number': order.order_number
        }, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'already paid' in str(response.data).lower()

        # Stripe should NOT be called for already-paid orders
        mock_stripe.assert_not_called()

    @patch('apps.payments.views.stripe.PaymentIntent.create')
    def test_create_payment_intent_no_auth(self, mock_stripe, api_client, order):
        """Test: Unauthenticated request returns 401."""
        response = api_client.post('/api/payments/create-intent/', {
            'order_number': order.order_number
        }, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        mock_stripe.assert_not_called()

    @patch('apps.payments.views.stripe.PaymentIntent.create')
    def test_create_payment_intent_wrong_order(self, mock_stripe, auth_client):
        """Test: Order not found returns 404."""
        mock_stripe.return_value = MagicMock(
            id='pi_test_999',
            client_secret='pi_test_secret'
        )

        response = auth_client.post('/api/payments/create-intent/', {
            'order_number': 'QM-DOESNOTEXIST'
        }, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND
        mock_stripe.assert_not_called()


@pytest.mark.django_db
class TestPaymentStatus:
    """Tests for payment status endpoint."""

    def test_get_payment_status_no_payment(self, auth_client, order):
        """Test: Order with no payment returns no_payment_found."""
        response = auth_client.get(f'/api/payments/{order.order_number}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['order_number'] == order.order_number
        assert response.data['payment_status'] == 'no_payment_found'

    def test_get_payment_status_with_payment(self, auth_client, order):
        """Test: Order with payment returns payment details."""
        # Create a payment record first
        Payment.objects.create(
            order=order,
            stripe_payment_intent_id='pi_test_abc',
            amount=order.total,
            status='succeeded',
        )

        response = auth_client.get(f'/api/payments/{order.order_number}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['payment_status'] == 'succeeded'
        assert float(response.data['amount']) == float(order.total)

    def test_get_payment_status_wrong_user(self, api_client, seller_user, order):
        """Test: Cannot see another user's payment status."""
        api_client.force_authenticate(user=seller_user)

        response = api_client.get(f'/api/payments/{order.order_number}/')

        # Order belongs to customer_user, seller_user should get 404
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_payment_status_no_auth(self, api_client, order):
        """Test: Unauthenticated returns 401."""
        response = api_client.get(f'/api/payments/{order.order_number}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED