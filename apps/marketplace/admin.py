from django.contrib import admin
from .models import Artwork, SellerApplication


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'medium', 'price', 'is_sold', 'created_at')
    list_filter = ('medium', 'is_sold')
    list_editable = ('is_sold',)
    search_fields = ('title', 'artist__email')


@admin.register(SellerApplication)
class SellerApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'portfolio_url', 'submitted_at', 'reviewed')
    list_filter = ('reviewed',)
    list_editable = ('reviewed',)
    search_fields = ('name', 'email')
