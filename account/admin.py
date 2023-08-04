from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from account.models import CustomUser, Profile, ProfilePicture


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', )}),
    )


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Profile)
admin.site.register(ProfilePicture)
