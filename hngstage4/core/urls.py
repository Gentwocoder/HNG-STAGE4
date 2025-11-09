"""
URL configuration for core app (User Service)
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    health_check,
    UserRegistrationView,
    UserLoginView,
    UserLogoutView,
    UserProfileView,
    PasswordChangeView,
    NotificationPreferencesView,
    PushTokenViewSet,
)

# Router for ViewSets
router = DefaultRouter()
router.register(r'push-tokens', PushTokenViewSet, basename='push-token')

app_name = 'core'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health-check'),
    
    # Authentication endpoints
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),
    
    # Notification preferences
    path('preferences/', NotificationPreferencesView.as_view(), name='preferences'),
    
    # Push tokens (using router)
    path('', include(router.urls)),
]
