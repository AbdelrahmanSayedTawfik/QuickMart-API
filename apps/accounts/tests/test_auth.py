# ═══════════════════════════════════════════════════════════════
# apps/accounts/tests/test_auth.py
# ═══════════════════════════════════════════════════════════════
#
# Tests for authentication endpoints:
# - Registration
# - Login
# - Token refresh
# - Password change
# ═══════════════════════════════════════════════════════════════

import pytest
from django.urls import reverse
from rest_framework import status
from apps.accounts.models import CustomUser


# ─────────────────────────────────────────────────────────────
# MARKER: Tell pytest these tests need database access
# ─────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestRegistration:
    """
    Tests for POST /api/auth/register/
    
    A class groups related tests together.
    pytest creates a fresh database for each test method.
    """
    
    def test_register_success(self, api_client):
        """
        Test: Valid registration returns 201 + tokens.
        
        api_client: Fixture from conftest.py (unauthenticated)
        """
        # ─── ARRANGE ───
        # Prepare test data
        payload = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Test@1234',
            'password2': 'Test@1234',
            'role': 'customer'
        }
        
        # ─── ACT ───
        # Make the request
        response = api_client.post('/api/auth/register/', payload, format='json')
        
        # ─── ASSERT ───
        # Verify the response
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data, "Access token not in response"
        assert 'refresh' in response.data, "Refresh token not in response"
        assert response.data['user']['username'] == 'newuser'
        
        # Verify user was created in database
        user = CustomUser.objects.get(username='newuser')
        assert user.email == 'new@test.com'
        assert user.check_password('Test@1234')
        assert user.role == 'customer'
    
    def test_register_password_mismatch(self, api_client):
        """
        Test: Passwords that don't match return 400.
        """
        payload = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'Test@1234',
            'password2': 'Different@1234',  # Mismatch!
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_str = str(response.data).lower()
        assert (
            'password' in response_str or
            'non_field_errors' in response_str or
            'do not match' in response_str or
            'mismatch' in response_str
        ), f"Expected password error but got: {response.data}"

    
    def test_register_duplicate_email(self, api_client, customer_user):
        """
        Test: Email already in use returns 400.
        
        customer_user: Fixture from conftest.py (pre-existing user)
        """
        payload = {
            'username': 'anotheruser',
            'email': customer_user.email,  # Already exists!
            'password': 'Test@1234',
            'password2': 'Test@1234',
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'email' in str(response.data).lower()
    
    def test_register_weak_password(self, api_client):
        """
        Test: Weak password returns 400.
        """
        payload = {
            'username': 'newuser',
            'email': 'new@test.com',
            'password': '123',  # Too weak!
            'password2': '123',
            'role': 'customer'
        }
        
        response = api_client.post('/api/auth/register/', payload, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLogin:
    """
    Tests for POST /api/auth/login/
    """
    
    def test_login_success(self, api_client, customer_user):
        """
        Test: Valid credentials return tokens.
        """
        payload = {
            'username': 'customer1',
            'password': 'Test@1234'
        }
        
        response = api_client.post('/api/auth/login/', payload, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
    
    def test_login_invalid_password(self, api_client, customer_user):
        """
        Test: Wrong password returns 401.
        """
        payload = {
            'username': 'customer1',
            'password': 'WrongPassword123!'
        }
        
        response = api_client.post('/api/auth/login/', payload, format='json')
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefresh:
    """
    Tests for POST /api/auth/token/refresh/
    """
    
    def test_refresh_success(self, api_client, customer_user):
        """
        Test: Valid refresh token returns new access token.
        """
        # First login to get refresh token
        login_response = api_client.post('/api/auth/login/', {
            'username': 'customer1',
            'password': 'Test@1234'
        }, format='json')
        
        refresh_token = login_response.data['refresh']
        
        # Now refresh
        response = api_client.post('/api/auth/token/refresh/', {
            'refresh': refresh_token
        }, format='json')
        
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data