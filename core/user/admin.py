from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import (
    User,
    UserProfile,
)




class UserProfileInline(admin.StackedInline):
    model = UserProfile




# USER ADMIN PANEL #

class UserAdmin(BaseUserAdmin):

    fieldsets = (
        ('User Information', {'fields': (
        'email', 'username', 'first_name', 'last_name', 
        'user_id', 'password', 'last_login'
        )}),

        ('Permissions', {'fields': (
        'is_active', 'is_staff', 'is_admin', 'is_superuser',
        'groups', 'user_permissions',
        )}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide', 'extrapretty',),
                'fields': ('email', 'username', 'password1', 'password2')
            }
        ),
    )

    list_display = ('email', 'username', 'user_id', 'is_active', 'last_login')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('email', 'user_id')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ("user_id",)

    inlines = [UserProfileInline]




# USER PROFILE ADMIN PANEL #
class UserProfileAdmin(admin.ModelAdmin):

    list_display = ('user', 'country', 'user_type', 'user_plan', 'is_verified')
    list_filter = ('user_type', 'user_plan', 'is_verified')
    ordering = ('-date_joined',)
    search_fields = ['user', 'business_id']




admin.site.register(User, UserAdmin)
admin.site.register(UserProfile, UserProfileAdmin)