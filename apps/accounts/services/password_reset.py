import secrets
from datetime import timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.accounts.models.password_reset import PasswordResetToken
from apps.accounts.models.user import CustomUser

class PasswordResetService:

    @staticmethod
    def request_reset(email):
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return

        PasswordResetToken.objects.filter(user=user).delete()

        token = secrets.token_hex(32)

        PasswordResetToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        message = (
            f"Hi {user.username},\n\n"
            f"You requested a password reset.\n\n"
            f"Your reset token (valid for 15 minutes):\n\n"
            f"{token}\n\n"                          
            f"Or click this link:\n"
            f"{reset_link}\n\n"
            f"If you did not request this, ignore this email.\n"
            f"Your password will not change."
        )

        send_mail(
            subject="Reset your password",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

    @staticmethod
    def confirm_reset(token, new_password, refresh_token=None):
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token
            )
        except PasswordResetToken.DoesNotExist:
            raise ValueError("Invalid or expired token.")

        if reset_token.is_expired():
            reset_token.delete()
            raise ValueError("Token has expired. Please request a new one.")

        if reset_token.is_used:
            raise ValueError("Token has already been used.")

        user = reset_token.user
        user.set_password(new_password)
        user.save()

        if refresh_token:
            from apps.accounts.services.auth import AuthService
            from django.core.exceptions import ValidationError
            try:
                AuthService.blacklist_token(refresh_token)
            except Exception as e:
                raise ValidationError(f"Failed to blacklist token: {e}") from e

        reset_token.is_used = True
        reset_token.save()