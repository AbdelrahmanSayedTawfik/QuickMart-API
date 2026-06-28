# apps/accounts/services/auth.py

from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache


class AuthService:

    @staticmethod
    def get_tokens_for_user(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @staticmethod
    def blacklist_token(refresh_token: str, access_token: str = None):

        # ── Refresh token → SimpleJWT blacklist table ──────────────────
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError as e:
            raise Exception(str(e))

        # ── Access token → Redis blocklist ─────────────────────────────
        if access_token:
            try:
                decoded = AccessToken(access_token)
                jti        = decoded['jti']
                # remaining lifetime in seconds
                import datetime
                exp        = decoded['exp']
                now        = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
                ttl        = int(exp - now)

                if ttl > 0:

                    cache.set(f'blocklist_jti_{jti}', '1', timeout=ttl)
            except Exception:
                pass  