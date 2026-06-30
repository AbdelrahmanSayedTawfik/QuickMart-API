# apps/accounts/views/logout.py

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
from apps.accounts.services.auth import AuthService


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Logout user',
        description='''
        Blacklist the refresh token and invalidate the access token immediately.
        Send both tokens in the request body.
        ''',
        request={'type': 'object', 'properties': {
            'refresh': {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJhbGc...'},
            'access':  {'type': 'string', 'example': 'eyJ0eXAiOiJKV1QiLCJhbGc...'},
        }},
        responses={
            205: OpenApiResponse(description='Logout successful'),
            400: OpenApiResponse(description='Invalid token'),
        }
    )
)
class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh')
        access_token  = request.data.get('access')   

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            AuthService.blacklist_token(
                refresh_token=refresh_token,
                access_token=access_token
            )
            return Response(
                {'detail': 'Logout successful.'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )