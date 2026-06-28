from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
from apps.accounts.serializers.password_reset import (
    RequestPasswordResetSerializer,
    ConfirmPasswordResetSerializer
)
from apps.accounts.services.password_reset import PasswordResetService


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Request password reset',
        description='''
        Send a password reset link to the user's email.
        
        - If the email exists, a reset link is sent (valid 15 minutes).
        - If the email does not exist, we still return 200 (security reason).
        ''',
        request=RequestPasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                description='Reset email sent (or silently ignored if email not found)',
                examples=[OpenApiExample('Success', value={
                    'detail': 'If this email exists, a reset link has been sent.'
                })]
            ),
        }
    )
)
class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class   = RequestPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        
        PasswordResetService.request_reset(
            email=serializer.validated_data['email']
        )

        
        return Response(
            {'detail': 'If this email exists, a reset link has been sent.'},
            status=status.HTTP_200_OK
        )


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='Confirm password reset',
        description='''
        Reset the password using the token received in email.
        
        Token expires after 15 minutes and can only be used once.
        ''',
        request=ConfirmPasswordResetSerializer,
        responses={
            200: OpenApiResponse(
                examples=[OpenApiExample('Success', value={
                    'detail': 'Password reset successful.'
                })]
            ),
            400: OpenApiResponse(
                description='Invalid or expired token',
                examples=[OpenApiExample('Error', value={
                    'detail': 'Token has expired. Please request a new one.'
                })]
            ),
        }
    )
)
class ConfirmPasswordResetView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class   = ConfirmPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            PasswordResetService.confirm_reset(
                token        = serializer.validated_data['token'],
                new_password = serializer.validated_data['new_password'],
                refresh_token= serializer.validated_data.get('refresh'),  
            )
        except ValueError as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'detail': 'Password reset successful.'},
            status=status.HTTP_200_OK
        )