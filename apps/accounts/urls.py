from django.contrib import admin
from django.urls import path, include
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.LoginView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
    path('auth/logout/', views.logout_view.as_view(), name='logout'),
    path('auth/me/', views.MeView.as_view(), name='me'),
    path('auth/me/update/', views.UpdateMeView.as_view(), name='update_me'),
    path('auth/me/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
]
