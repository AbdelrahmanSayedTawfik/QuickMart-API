from rest_framework_simplejwt.tokens import RefreshToken
from apps.accounts.models.user import CustomUser

class AuthService:
    @staticmethod
    def get_tokens_for_user(user: CustomUser) -> dict:
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    @staticmethod
    def blacklist_token(refresh_token: str) -> None:
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            raise ValueError("Invalid token") from e    