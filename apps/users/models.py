from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=True)


class ArtistProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='artist_profile')
    display_name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    medium = models.CharField(max_length=100, blank=True, help_text='e.g. Ceramics, Printmaking, Oil')
    profile_photo = models.ImageField(upload_to='artists/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.display_name
