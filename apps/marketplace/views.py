from django.shortcuts import render
from .models import Artwork


def home(request):
    return render(request, 'home.html')


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
