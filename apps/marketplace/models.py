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
        ('glass', 'Glass'),
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


class SellerApplication(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    portfolio_url = models.URLField(blank=True)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.name} — {self.email}'


class Order(models.Model):
    artwork = models.ForeignKey(Artwork, on_delete=models.PROTECT, related_name='orders')
    buyer_email = models.EmailField()
    stripe_session_id = models.CharField(max_length=200, unique=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    shipping_name = models.CharField(max_length=200, blank=True)
    shipping_address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order {self.pk} — {self.artwork.title}'
