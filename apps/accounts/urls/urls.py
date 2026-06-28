from django.urls import path
from apps.accounts.apis.register import RegisterView
from apps.accounts.apis.login import LoginView
from apps.accounts.apis.logout import LogoutView
from apps.accounts.apis.update import MeView , UpdateMeView
from apps.accounts.apis.change import ChangePasswordView
from apps.accounts.apis.password_reset import RequestPasswordResetView
from apps.accounts.apis.password_reset import ConfirmPasswordResetView


urlpatterns = [
    path('auth/',RegisterView.as_view(),name='auth'),  # DONE 
    path('auth/logout/', LogoutView.as_view(), name='logout'), #DONE
    path('users/', LoginView.as_view(), name='users'), #DONE
    path('me/', MeView.as_view(), name='me'),  #DONE
    path('me/update/', UpdateMeView.as_view(), name='update-me'),  #DONE 
    path('me/password/', ChangePasswordView.as_view(), name='change-password'), #DONE
    path('auth/password-reset/',RequestPasswordResetView.as_view()),
    path('auth/password-reset/confirm/', ConfirmPasswordResetView.as_view()),
]
