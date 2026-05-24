from django.shortcuts import render
from .serializers import RegisterSerializer , UpdateUserSerializer
from rest_framework import generics
from .models import CustomUser
from rest_framework.permissions import AllowAny , IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)


# Create your views here.

@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Register new user',
        description='''
        Create a new user account with username, email, and password.
        
        Password requirements:
        - Minimum 8 characters
        - At least one letter and one number
        
        Returns JWT tokens for immediate authentication.
        ''',
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(
                description='User created successfully',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'user': {
                                'id': 1,
                                'username': 'john_doe',
                                'email': 'john@example.com',
                                'role': 'customer'
                            },
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    )
                ]
            ),
            400: OpenApiResponse(
                description='Validation error',
                examples=[
                    OpenApiExample(
                        'Email exists',
                        value={'email': ['User with this email already exists.']}
                    ),
                    OpenApiExample(
                        'Password mismatch',
                        value={'password2': ['Passwords do not match.']}
                    )
                ]
            ),
        }
    )
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': RegisterSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        },status=201)
    
    


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Logout user',
        description='''
        Blacklist the refresh token to prevent future use.
        
        Requires authentication. Send the refresh token in request body.
        ''',
        request={'type': 'object', 'properties': {
            'refresh': {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJhbGc...'}
        }},
        responses={
            205: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid token'),
        }
    )
)
class logout_view(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=205)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400
            )
        

@extend_schema_view(
    get=extend_schema(
        tags=['Users'],
        summary='Get current user profile',
        description='Returns the authenticated user\'s profile information.',
        responses={
            200: OpenApiResponse(
                description='User profile',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'id': 1,
                            'username': 'john_doe',
                            'email': 'john@example.com',
                            'role': 'customer',
                            'first_name': 'John',
                            'last_name': 'Doe'
                        }
                    )
                ]
            ),
            401: OpenApiResponse(description='Not authenticated'),
        }
    )
)
class MeView(generics.RetrieveAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    
@extend_schema_view(
    put=extend_schema(
        tags=['Users'],
        summary='Update user profile',
        description='Update current user\'s profile information.',
        request=UpdateUserSerializer,
        responses={
            200: OpenApiResponse(description='Profile updated'),
            400: OpenApiResponse(description='Validation error'),
        }
    ),
    patch=extend_schema(
        tags=['Users'],
        summary='Partially update profile',
        description='Update specific fields of user profile.',
        request=UpdateUserSerializer,
        responses={
            200: OpenApiResponse(description='Profile updated'),
        }
    )
)
class UpdateMeView(generics.UpdateAPIView):
    serializer_class = UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    
@extend_schema_view(
    post=extend_schema(
        tags=['Users'],
        summary='Change password',
        description='''
        Change current user's password.
        
        Requires old password for security verification.
        ''',
        request={'type': 'object', 'properties': {
            'old_password': {'type': 'string', 'example': 'OldPass123!'},
            'new_password': {'type': 'string', 'example': 'NewPass456!'}
        }},
        responses={
            200: OpenApiResponse(
                description='Password changed',
                examples=[OpenApiExample('Success', value={'detail': 'Password changed successfully.'})]
            ),
            400: OpenApiResponse(
                description='Invalid old password',
                examples=[OpenApiExample('Wrong password', value={'detail': 'Old password is incorrect.'})]
            ),
        }
    )
)
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"detail": "Old password is incorrect."}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password changed successfully."}, status=200)
    
    


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Login user',
        description='''
        Authenticate with username and password.
        
        Returns JWT access and refresh tokens.
        Use access token in `Authorization: Bearer <token>` header.
        ''',
        request=TokenObtainPairSerializer,
        responses={
            200: OpenApiResponse(
                description='Login successful',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={
                            'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
                            'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...'
                        }
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Invalid credentials',
                examples=[
                    OpenApiExample(
                        'Wrong password',
                        value={'detail': 'No active account found with the given credentials'}
                    )
                ]
            ),
        }
    )
)
class LoginView(TokenObtainPairView):
    """
    Obtain JWT tokens with username and password.
    
    Subclass of TokenObtainPairView from simplejwt.
    """
    pass


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Refresh access token',
        description='''
        Get a new access token using a valid refresh token.
        
        Use this when access token expires (typically after 5 minutes).
        ''',
        request={'type': 'object', 'properties': {
            'refresh': {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJhbGc...'}
        }},
        responses={
            200: OpenApiResponse(
                description='New access token',
                examples=[
                    OpenApiExample(
                        'Success',
                        value={'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...'}
                    )
                ]
            ),
            401: OpenApiResponse(
                description='Invalid or expired refresh token'
            ),
        }
    )
)
class RefreshTokenView(TokenRefreshView):
    """
    Refresh JWT access token.
    
    Subclass of TokenRefreshView from simplejwt.
    """
    pass
    
    