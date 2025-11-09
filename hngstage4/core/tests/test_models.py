"""
Test cases for User Service models
"""
import pytest
from django.contrib.auth import get_user_model
from core.models import UserProfile, NotificationPreference, PushToken

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:
    """Test User model"""
    
    def test_create_user(self):
        """Test creating a user"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        assert user.email == 'test@example.com'
        assert user.username == 'testuser'
        assert user.check_password('testpass123')
        assert not user.is_verified
        assert user.is_active
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='adminpass123'
        )
        
        assert user.is_staff
        assert user.is_superuser
        assert user.is_active


@pytest.mark.django_db
class TestUserProfile:
    """Test UserProfile model"""
    
    def test_create_profile(self):
        """Test creating a user profile"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        profile = UserProfile.objects.create(
            user=user,
            first_name='John',
            last_name='Doe'
        )
        
        assert profile.full_name == 'John Doe'
        assert profile.user == user
    
    def test_profile_full_name_fallback(self):
        """Test full_name property with empty names"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        profile = UserProfile.objects.create(user=user)
        
        assert profile.full_name == 'testuser'


@pytest.mark.django_db
class TestNotificationPreference:
    """Test NotificationPreference model"""
    
    def test_create_preferences(self):
        """Test creating notification preferences"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        prefs = NotificationPreference.objects.create(user=user)
        
        assert prefs.email_enabled
        assert prefs.push_enabled
        assert prefs.frequency_limit == 50
    
    def test_is_email_allowed(self):
        """Test email permission checking"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        prefs = NotificationPreference.objects.create(
            user=user,
            email_enabled=True,
            email_marketing=False
        )
        
        assert prefs.is_email_allowed('transactional')
        assert not prefs.is_email_allowed('marketing')


@pytest.mark.django_db
class TestPushToken:
    """Test PushToken model"""
    
    def test_create_push_token(self):
        """Test creating a push token"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        token = PushToken.objects.create(
            user=user,
            token='test_token_12345',
            platform='android',
            token_type='fcm',
            device_name='Samsung Galaxy'
        )
        
        assert token.user == user
        assert token.is_active
        assert token.platform == 'android'
