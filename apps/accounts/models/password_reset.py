from django.db import models
from apps.accounts.models.user import CustomUser
from django.utils import timezone




class PasswordResetToken(models.Model):
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reset_tokens')
    token      = models.CharField(max_length=200, unique=True)
    expires_at = models.DateTimeField()
    is_used    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.email}"