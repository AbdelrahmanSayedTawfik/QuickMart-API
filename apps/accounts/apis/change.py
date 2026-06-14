from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample


@extend_schema_view(
    post=extend_schema(
        tags=['Users'],
        summary='Change password',
        description='Change current user\'s password. Requires old password.',
        request={'type': 'object', 'properties': {
            'old_password': {'type': 'string', 'example': 'OldPass123!'},
            'new_password': {'type': 'string', 'example': 'NewPass456!'}
        }},
        responses={
            200: OpenApiResponse(examples=[OpenApiExample('Success', value={
                'detail': 'Password changed successfully.'
            })]),
            400: OpenApiResponse(description='Invalid old password'),
        }
    )
)
class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        
        # Validation: check old password
        if not user.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Business logic: change password
        user.set_password(new_password)
        user.save()
        
        return Response(
            {"detail": "Password changed successfully."},
            status=status.HTTP_200_OK
        )