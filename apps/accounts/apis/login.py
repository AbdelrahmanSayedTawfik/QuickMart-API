from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
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
        summary='Login user',
        description='''
        Authenticate with username and password.
        
        Returns JWT access and refresh tokens.
        Use access token in `Authorization: Bearer <token>` header.
        ''',
        
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
    pass



