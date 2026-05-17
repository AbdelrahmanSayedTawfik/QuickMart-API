
from django.contrib import admin
from django.urls import path , include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)



urlpatterns = [
    path('admin/', admin.site.urls),
        # Schema (the raw JSON file)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    
    # Swagger UI (the beautiful interface)
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # ReDoc (alternative documentation UI - cleaner, read-only)
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.products.urls')),
    path('api/', include('apps.orders.urls')),
]
