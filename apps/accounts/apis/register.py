from apps.accounts.serializers.register import RegisterSerializer
from rest_framework import status , generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.accounts.services.auth import AuthService
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
)




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
        
        # Generate JWT tokens for the new user
        tokens = AuthService.get_tokens_for_user(user)
        
        response_data = {
            'user': RegisterSerializer(user).data,
            'refresh': tokens['refresh'],
            'access': tokens['access']
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)