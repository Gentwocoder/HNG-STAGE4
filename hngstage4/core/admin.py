from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile, NotificationPreference, PushToken


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for User model"""
    list_display = ['email', 'username', 'is_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'phone_number']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('phone_number', 'is_verified')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'last_login_ip')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin configuration for UserProfile model"""
    list_display = ['user', 'full_name', 'timezone', 'language', 'created_at']
    list_filter = ['timezone', 'language', 'created_at']
    search_fields = ['user__email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Profile Info', {'fields': ('first_name', 'last_name', 'avatar_url', 'bio')}),
        ('Settings', {'fields': ('timezone', 'language')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin configuration for NotificationPreference model"""
    list_display = ['user', 'email_enabled', 'push_enabled', 'frequency_limit']
    list_filter = ['email_enabled', 'push_enabled', 'created_at']
    search_fields = ['user__email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Email Preferences', {
            'fields': ('email_enabled', 'email_marketing', 'email_transactional', 
                      'email_security', 'email_system')
        }),
        ('Push Preferences', {
            'fields': ('push_enabled', 'push_marketing', 'push_transactional',
                      'push_security', 'push_system')
        }),
        ('General Settings', {
            'fields': ('do_not_disturb_start', 'do_not_disturb_end', 'frequency_limit')
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PushToken)
class PushTokenAdmin(admin.ModelAdmin):
    """Admin configuration for PushToken model"""
    list_display = ['user', 'platform', 'token_type', 'is_active', 'device_name', 'last_used']
    list_filter = ['platform', 'token_type', 'is_active', 'created_at']
    search_fields = ['user__email', 'device_id', 'device_name']
    ordering = ['-created_at']
    
    fieldsets = (
        ('User', {'fields': ('user',)}),
        ('Token Info', {'fields': ('token', 'token_type', 'platform')}),
        ('Device Info', {'fields': ('device_id', 'device_name', 'is_active')}),
        ('Timestamps', {'fields': ('last_used', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['last_used', 'created_at', 'updated_at']
