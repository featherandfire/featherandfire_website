from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, ArtistProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Roles', {'fields': ('is_seller', 'is_buyer')}),
    )


@admin.register(ArtistProfile)
class ArtistProfileAdmin(admin.ModelAdmin):
    list_display = ('display_name', 'user', 'medium', 'location', 'is_featured')
    list_filter = ('is_featured', 'medium')
    list_editable = ('is_featured',)
    search_fields = ('display_name', 'user__email')
