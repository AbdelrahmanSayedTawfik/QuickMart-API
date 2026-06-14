from django.urls import path
from apps.accounts.apis.register import RegisterView
from apps.accounts.apis.login import LoginView
from apps.accounts.apis.logout import LogoutView
from apps.accounts.apis.update import MeView , UpdateMeView
from apps.accounts.apis.change import ChangePasswordView


urlpatterns = [
    path('/auth',RegisterView.as_view(),name='auth'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('users/', RegisterView.as_view(), name='users'),
    path('me/', MeView.as_view(), name='me'),
    path('me/', UpdateMeView.as_view(), name='update-me'),     
    path('me/password/', ChangePasswordView.as_view(), name='change-password'),
]
