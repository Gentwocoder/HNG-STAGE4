from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import NotificationPreference, PushToken, User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile model"""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "full_name",
            "avatar_url",
            "timezone",
            "language",
            "bio",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""

    class Meta:
        model = NotificationPreference
        fields = [
            "id",
            "email_enabled",
            "email_marketing",
            "email_transactional",
            "email_security",
            "email_system",
            "push_enabled",
            "push_marketing",
            "push_transactional",
            "push_security",
            "push_system",
            "do_not_disturb_start",
            "do_not_disturb_end",
            "frequency_limit",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class PushTokenSerializer(serializers.ModelSerializer):
    """Serializer for PushToken model"""

    class Meta:
        model = PushToken
        fields = [
            "id",
            "token",
            "token_type",
            "platform",
            "device_id",
            "device_name",
            "is_active",
            "last_used",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "last_used", "created_at", "updated_at"]
        extra_kwargs = {"token": {"write_only": True}}

    def validate_token(self, value):
        """Ensure token is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Token cannot be empty")
        return value.strip()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model with nested profile and preferences"""

    profile = UserProfileSerializer(read_only=True)
    notification_preferences = NotificationPreferenceSerializer(read_only=True)
    push_tokens_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "phone_number",
            "is_verified",
            "is_active",
            "created_at",
            "updated_at",
            "last_login",
            "profile",
            "notification_preferences",
            "push_tokens_count",
        ]
        read_only_fields = ["id", "is_verified", "created_at", "updated_at", "last_login"]

    def get_push_tokens_count(self, obj):
        """Get count of active push tokens"""
        return obj.push_tokens.filter(is_active=True).count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    password_confirm = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "email",
            "username",
            "password",
            "password_confirm",
            "phone_number",
            "first_name",
            "last_name",
        ]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate(self, attrs):
        """Validate that passwords match"""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_email(self, value):
        """Ensure email is lowercase and unique"""
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        """Ensure username is unique"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def create(self, validated_data):
        """Create user with profile and notification preferences"""
        validated_data.pop("password_confirm")
        first_name = validated_data.pop("first_name", "")
        last_name = validated_data.pop("last_name", "")

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create profile
        UserProfile.objects.create(user=user, first_name=first_name, last_name=last_name)

        # Create default notification preferences
        NotificationPreference.objects.create(user=user)

        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Authenticate user credentials"""
        email = attrs.get("email", "").lower()
        password = attrs.get("password")

        if email and password:
            user = authenticate(
                request=self.context.get("request"), username=email, password=password
            )

            if not user:
                raise serializers.ValidationError("Unable to log in with provided credentials.")

            if not user.is_active:
                raise serializers.ValidationError("User account is disabled.")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'.")

        attrs["user"] = user
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""

    old_password = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={"input_type": "password"},
    )
    new_password_confirm = serializers.CharField(
        required=True, write_only=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        """Validate passwords"""
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError({"new_password": "New password fields didn't match."})
        return attrs

    def validate_old_password(self, value):
        """Check that old password is correct"""
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user information"""

    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ["username", "phone_number", "profile"]

    def update(self, instance, validated_data):
        """Update user and profile"""
        profile_data = validated_data.pop("profile", None)

        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update profile if provided
        if profile_data and hasattr(instance, "profile"):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
