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

    pass

