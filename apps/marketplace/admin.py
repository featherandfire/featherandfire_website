from django.contrib import admin
from .models import Artwork, SellerApplication, Order


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


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('pk', 'artwork', 'buyer_email', 'amount', 'paid', 'created_at')
    list_filter = ('paid',)
    search_fields = ('buyer_email', 'artwork__title', 'stripe_session_id')
