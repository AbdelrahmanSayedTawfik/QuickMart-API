from apps.accounts.serializers.register import RegisterSerializer
from apps.accounts.serializers.update import UpdateUserSerializer
from rest_framework import status , generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
    OpenApiExample,
    OpenApiResponse,
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
    