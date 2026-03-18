from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Artwork
from .forms import SellerApplicationForm
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


def apply(request):
    if request.method == 'POST':
        form = SellerApplicationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your application has been submitted. We\'ll be in touch soon.')
            return redirect('apply')
    else:
        form = SellerApplicationForm()
    return render(request, 'apply.html', {'form': form})


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
