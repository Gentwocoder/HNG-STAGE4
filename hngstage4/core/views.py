import logging
import time

from django.contrib.auth import logout
from django.core.paginator import EmptyPage, Paginator
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .cache_manager import CacheManager, RateLimiter
from .message_queue import mq_manager
from .models import NotificationPreference, PushToken, User
from .response_utils import APIResponse, calculate_pagination_meta
from .serializers import (
    NotificationPreferenceSerializer,
    PasswordChangeSerializer,
    PushTokenSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

logger = logging.getLogger(__name__)


# ============== Health Check ==============


@api_view(["GET"])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring
    Returns service status and basic metrics
    """
    start_time = time.time()

    health_status = {
        "service": "user-service",
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0",
        "checks": {
            "database": "healthy",
            "cache": "healthy",
        },
    }

    # Check database
    try:
        User.objects.first()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Database health check failed: {e}")

    # Check cache
    try:
        CacheManager.set("health_check", "test", 10)
        CacheManager.get("health_check")
        health_status["checks"]["cache"] = "healthy"
    except Exception as e:
        health_status["checks"]["cache"] = "unhealthy"
        health_status["status"] = "degraded"
        logger.error(f"Cache health check failed: {e}")

    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    health_status["response_time_ms"] = round(response_time, 2)

    return APIResponse.success(data=health_status, message="Health check completed")


# ============== Authentication Views ==============


class UserRegistrationView(APIView):
    """
    API endpoint for user registration
    POST /api/v1/users/register/
    """

    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserSerializer},
        tags=["Authentication"],
        description="Register a new user account",
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Check rate limit
            ip_address = request.META.get("REMOTE_ADDR", "unknown")
            if not RateLimiter.is_allowed(ip_address, "registration", 5, 3600):
                return APIResponse.error(
                    error="Too many registration attempts. Please try again later.",
                    message="Rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            user = serializer.save()

            # Publish user registration event to RabbitMQ
            mq_manager.publish_user_registered(
                user_id=str(user.user_id), email=user.email, username=user.username
            )

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            user_data = UserSerializer(user).data
            user_data["tokens"] = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            logger.info(f"New user registered: {user.email}")

            return APIResponse.created(data=user_data, message="User registered successfully")

        return APIResponse.validation_error(serializer.errors)


class UserLoginView(APIView):
    """
    API endpoint for user login
    POST /api/v1/users/login/
    """

    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    @extend_schema(
        request=UserLoginSerializer,
        responses={200: UserSerializer},
        tags=["Authentication"],
        description="Authenticate user and return JWT tokens",
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = serializer.validated_data["user"]

            # Check rate limit
            if not RateLimiter.is_allowed(str(user.id), "login", 10, 300):
                return APIResponse.error(
                    error="Too many login attempts. Please try again later.",
                    message="Rate limit exceeded",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Update last login IP
            ip_address = request.META.get("REMOTE_ADDR")
            if ip_address:
                user.last_login_ip = ip_address
                user.save(update_fields=["last_login_ip", "last_login"])

            # Generate tokens
            refresh = RefreshToken.for_user(user)

            user_data = UserSerializer(user).data
            user_data["tokens"] = {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }

            # Cache user data
            CacheManager.set_user(str(user.id), user_data)

            logger.info(f"User logged in: {user.email}")

            return APIResponse.success(data=user_data, message="Login successful")

        return APIResponse.validation_error(serializer.errors)


class UserLogoutView(APIView):
    """
    API endpoint for user logout
    POST /api/v1/users/logout/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")

            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()

            # Invalidate cache
            CacheManager.invalidate_user_cache(str(request.user.id))

            logout(request)

            logger.info(f"User logged out: {request.user.email}")

            return APIResponse.success(message="Logout successful")

        except Exception as e:
            logger.error(f"Logout error: {e}")
            return APIResponse.error(
                error="Logout failed", message="An error occurred during logout"
            )


# ============== User Management Views ==============


class UserProfileView(APIView):
    """
    API endpoint for user profile management
    GET /api/v1/users/profile/ - Get current user profile
    PUT /api/v1/users/profile/ - Update current user profile
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserProfileSerializer

    def get(self, request):
        """Get current user profile"""
        user = request.user

        # Try to get from cache first
        cached_data = CacheManager.get_user(str(user.id))
        if cached_data:
            return APIResponse.success(
                data=cached_data, message="User profile retrieved from cache"
            )

        user_data = UserSerializer(user).data

        # Cache the data
        CacheManager.set_user(str(user.id), user_data)

        return APIResponse.success(data=user_data, message="User profile retrieved successfully")

    def put(self, request):
        """Update current user profile"""
        user = request.user

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            # Get changed fields before save
            changed_fields = {}
            for field, value in serializer.validated_data.items():
                if getattr(user, field) != value:
                    changed_fields[field] = value

            serializer.save()

            # Publish user update event
            if changed_fields:
                mq_manager.publish_user_updated(
                    user_id=str(user.user_id), updated_fields=changed_fields
                )

            # Invalidate cache
            CacheManager.invalidate_user_cache(str(user.id))

            user_data = UserSerializer(user).data

            logger.info(f"User profile updated: {user.email}")

            return APIResponse.success(data=user_data, message="Profile updated successfully")

        return APIResponse.validation_error(serializer.errors)


class PasswordChangeView(APIView):
    """
    API endpoint for password change
    POST /api/v1/users/change-password/
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})

        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data["new_password"])
            user.save()

            # Invalidate cache
            CacheManager.invalidate_user_cache(str(user.id))

            logger.info(f"Password changed for user: {user.email}")

            return APIResponse.success(message="Password changed successfully")

        return APIResponse.validation_error(serializer.errors)


# ============== Notification Preferences Views ==============


class NotificationPreferencesView(APIView):
    """
    API endpoint for notification preferences
    GET /api/v1/users/preferences/ - Get preferences
    PUT /api/v1/users/preferences/ - Update preferences
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get user notification preferences"""
        user = request.user

        # Try to get from cache first
        cached_prefs = CacheManager.get_user_preferences(str(user.id))
        if cached_prefs:
            return APIResponse.success(
                data=cached_prefs, message="Preferences retrieved from cache"
            )

        try:
            preferences = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            # Create default preferences if not exists
            preferences = NotificationPreference.objects.create(user=user)

        serializer = NotificationPreferenceSerializer(preferences)

        # Cache preferences
        CacheManager.set_user_preferences(str(user.id), serializer.data)

        return APIResponse.success(
            data=serializer.data, message="Preferences retrieved successfully"
        )

    def put(self, request):
        """Update user notification preferences"""
        user = request.user

        try:
            preferences = user.notification_preferences
        except NotificationPreference.DoesNotExist:
            preferences = NotificationPreference.objects.create(user=user)

        serializer = NotificationPreferenceSerializer(preferences, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # Publish preferences update event
            mq_manager.publish_preferences_updated(
                user_id=str(user.user_id), preferences=serializer.data
            )

            # Invalidate cache
            CacheManager.delete_user_preferences(str(user.id))

            logger.info(f"Preferences updated for user: {user.email}")

            return APIResponse.success(
                data=serializer.data, message="Preferences updated successfully"
            )

        return APIResponse.validation_error(serializer.errors)


# ============== Push Token Views ==============


class PushTokenViewSet(viewsets.ModelViewSet):
    """
    ViewSet for push token management
    GET /api/v1/users/push-tokens/ - List all tokens
    POST /api/v1/users/push-tokens/ - Create new token
    GET /api/v1/users/push-tokens/{id}/ - Get specific token
    PUT /api/v1/users/push-tokens/{id}/ - Update token
    DELETE /api/v1/users/push-tokens/{id}/ - Delete token
    """

    serializer_class = PushTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return tokens for current user only"""
        return PushToken.objects.filter(user=self.request.user)

    def list(self, request):
        """List all push tokens for current user"""
        queryset = self.get_queryset()

        # Pagination
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))

        paginator = Paginator(queryset, limit)

        try:
            page_obj = paginator.page(page)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        serializer = self.get_serializer(page_obj, many=True)
        meta = calculate_pagination_meta(page_obj, limit)

        return APIResponse.success(
            data=serializer.data, message="Push tokens retrieved successfully", meta=meta
        )

    def create(self, request):
        """Create new push token"""
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check if token already exists for this user
            existing_token = PushToken.objects.filter(
                user=request.user, token=serializer.validated_data["token"]
            ).first()

            if existing_token:
                # Update existing token
                for key, value in serializer.validated_data.items():
                    setattr(existing_token, key, value)
                existing_token.is_active = True
                existing_token.save()

                return APIResponse.success(
                    data=self.get_serializer(existing_token).data,
                    message="Push token updated successfully",
                )

            # Create new token
            token_instance = serializer.save(user=request.user)

            # Publish push token added event
            mq_manager.publish_push_token_added(
                user_id=str(request.user.user_id),
                token=token_instance.token,
                device_type=token_instance.device_type,
            )

            logger.info(f"Push token created for user: {request.user.email}")

            return APIResponse.created(
                data=serializer.data, message="Push token created successfully"
            )

        return APIResponse.validation_error(serializer.errors)

    def retrieve(self, request, pk=None):
        """Get specific push token"""
        try:
            token = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(token)

            return APIResponse.success(
                data=serializer.data, message="Push token retrieved successfully"
            )
        except PushToken.DoesNotExist:
            return APIResponse.not_found(error="Push token not found")

    def update(self, request, pk=None):
        """Update push token"""
        try:
            token = self.get_queryset().get(pk=pk)
            serializer = self.get_serializer(token, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()

                logger.info(f"Push token updated: {pk}")

                return APIResponse.success(
                    data=serializer.data, message="Push token updated successfully"
                )

            return APIResponse.validation_error(serializer.errors)

        except PushToken.DoesNotExist:
            return APIResponse.not_found(error="Push token not found")

    def destroy(self, request, pk=None):
        """Delete push token"""
        try:
            token = self.get_queryset().get(pk=pk)
            token_value = token.token  # Store before deletion

            token.delete()

            # Publish push token removed event
            mq_manager.publish_push_token_removed(
                user_id=str(request.user.user_id), token=token_value
            )

            logger.info(f"Push token deleted: {pk}")

            return APIResponse.no_content(message="Push token deleted successfully")

        except PushToken.DoesNotExist:
            return APIResponse.not_found(error="Push token not found")

    @action(detail=False, methods=["post"])
    def deactivate_all(self, request):
        """Deactivate all push tokens for current user"""
        count = self.get_queryset().update(is_active=False)

        logger.info(f"Deactivated {count} push tokens for user: {request.user.email}")

        return APIResponse.success(
            data={"deactivated_count": count},
            message=f"{count} push tokens deactivated successfully",
        )
