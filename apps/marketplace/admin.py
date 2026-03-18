from django.contrib import admin
from .models import Artwork


@admin.register(Artwork)
class ArtworkAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'medium', 'price', 'is_sold', 'created_at')
    list_filter = ('medium', 'is_sold')
    list_editable = ('is_sold',)
    search_fields = ('title', 'artist__email')
