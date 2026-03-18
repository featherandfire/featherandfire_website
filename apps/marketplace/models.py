from django.db import models
from django.conf import settings


class Artwork(models.Model):
    MEDIUM_CHOICES = [
        ('painting', 'Painting'),
        ('drawing', 'Drawing'),
        ('printmaking', 'Printmaking'),
        ('ceramics', 'Ceramics'),
        ('sculpture', 'Sculpture'),
        ('photography', 'Photography'),
        ('mixed_media', 'Mixed Media'),
        ('other', 'Other'),
    ]

    artist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='artworks',
        limit_choices_to={'is_seller': True},
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    medium = models.CharField(max_length=50, choices=MEDIUM_CHOICES, default='other')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image = models.ImageField(upload_to='artwork/')
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {self.artist}'
