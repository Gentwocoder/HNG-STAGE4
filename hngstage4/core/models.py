import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Manages user authentication and basic profile information.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()], db_index=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "users"
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    Extended user profile information.
    One-to-one relationship with User model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    avatar_url = models.URLField(blank=True, null=True)
    timezone = models.CharField(max_length=50, default="UTC")
    language = models.CharField(max_length=10, default="en")
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_profiles"

    def __str__(self):
        return f"Profile: {self.user.email}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.user.username


class NotificationPreference(models.Model):
    """
    User's notification preferences for different channels and types.
    """

    NOTIFICATION_TYPE_CHOICES = [
        ("all", "All Notifications"),
        ("marketing", "Marketing"),
        ("transactional", "Transactional"),
        ("security", "Security"),
        ("system", "System"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="notification_preferences"
    )

    # Email preferences
    email_enabled = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=True)
    email_transactional = models.BooleanField(default=True)
    email_security = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)

    # Push notification preferences
    push_enabled = models.BooleanField(default=True)
    push_marketing = models.BooleanField(default=False)
    push_transactional = models.BooleanField(default=True)
    push_security = models.BooleanField(default=True)
    push_system = models.BooleanField(default=True)

    # General settings
    do_not_disturb_start = models.TimeField(blank=True, null=True)
    do_not_disturb_end = models.TimeField(blank=True, null=True)
    frequency_limit = models.IntegerField(default=50, help_text="Max notifications per day")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "notification_preferences"

    def __str__(self):
        return f"Preferences: {self.user.email}"

    def is_email_allowed(self, notification_type="all"):
        """Check if email notifications are allowed for a specific type"""
        if not self.email_enabled:
            return False

        type_mapping = {
            "marketing": self.email_marketing,
            "transactional": self.email_transactional,
            "security": self.email_security,
            "system": self.email_system,
        }

        return type_mapping.get(notification_type, True)

    def is_push_allowed(self, notification_type="all"):
        """Check if push notifications are allowed for a specific type"""
        if not self.push_enabled:
            return False

        type_mapping = {
            "marketing": self.push_marketing,
            "transactional": self.push_transactional,
            "security": self.push_security,
            "system": self.push_system,
        }

        return type_mapping.get(notification_type, True)


class PushToken(models.Model):
    """
    Stores device push notification tokens for FCM, OneSignal, etc.
    Supports multiple devices per user.
    """

    PLATFORM_CHOICES = [
        ("web", "Web"),
        ("android", "Android"),
        ("ios", "iOS"),
    ]

    TOKEN_TYPE_CHOICES = [
        ("fcm", "Firebase Cloud Messaging"),
        ("onesignal", "OneSignal"),
        ("vapid", "Web Push VAPID"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="push_tokens")
    token = models.TextField(unique=True, db_index=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPE_CHOICES, default="fcm")
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES)
    device_id = models.CharField(max_length=255, blank=True)
    device_name = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "push_tokens"
        indexes = [
            models.Index(fields=["user", "is_active"]),
            models.Index(fields=["token"]),
        ]
        unique_together = [["user", "device_id", "platform"]]

    def __str__(self):
        return f"{self.user.email} - {self.platform} - {self.token[:20]}..."
