from django.shortcuts import render
from .models import Artwork
from apps.users.models import ArtistProfile


def home(request):
    featured_artists = ArtistProfile.objects.filter(is_featured=True).select_related('user')[:3]
    artwork_count = Artwork.objects.count()
    artist_count = ArtistProfile.objects.count()
    hero_artworks = Artwork.objects.filter(is_sold=False).exclude(image='').order_by('?')[:12]
    hero_artwork_urls = [a.image.url for a in hero_artworks]

    context = {
        'featured_artists': featured_artists,
        'artwork_count': artwork_count,
        'artist_count': artist_count,
        'hero_artworks': hero_artworks,
        'hero_artwork_urls': hero_artwork_urls,
    }
    return render(request, 'home.html', context)


def about(request):
    return render(request, 'about.html')


def gallery(request):
    artworks = Artwork.objects.select_related('artist__artist_profile').filter(is_sold=False)

    medium = request.GET.get('medium')
    if medium:
        artworks = artworks.filter(medium=medium)

    context = {
        'artworks': artworks,
        'medium_choices': Artwork.MEDIUM_CHOICES,
        'selected_medium': medium,
    }
    return render(request, 'gallery.html', context)
