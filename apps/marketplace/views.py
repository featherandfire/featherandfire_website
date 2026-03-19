import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Artwork, Order
from .forms import SellerApplicationForm
from apps.users.models import ArtistProfile

stripe.api_key = settings.STRIPE_SECRET_KEY


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


def checkout(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk, is_sold=False)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(artwork.price * 100),
                'product_data': {
                    'name': artwork.title,
                    'description': artwork.description[:255] if artwork.description else '',
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(f'/order/success/?session_id={{CHECKOUT_SESSION_ID}}'),
        cancel_url=request.build_absolute_uri(f'/artwork/{pk}/'),
        metadata={'artwork_id': pk},
    )
    Order.objects.create(
        artwork=artwork,
        buyer_email='',
        stripe_session_id=session.id,
        amount=artwork.price,
    )
    return redirect(session.url, permanent=False)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        try:
            sessions = stripe.checkout.Session.list(payment_intent=payment_intent['id'])
            if sessions.data:
                session = sessions.data[0]
                order = Order.objects.get(stripe_session_id=session['id'])
                order.paid = True
                order.buyer_email = session.get('customer_details', {}).get('email', '')
                order.save()
                order.artwork.is_sold = True
                order.artwork.save()
        except Order.DoesNotExist:
            pass

    return HttpResponse(status=200)


def order_success(request):
    session_id = request.GET.get('session_id')
    order = None
    if session_id:
        try:
            order = Order.objects.get(stripe_session_id=session_id)
        except Order.DoesNotExist:
            pass
    return render(request, 'order_success.html', {'order': order})


def artwork_detail(request, pk):
    artwork = get_object_or_404(Artwork, pk=pk)
    artist_profile = getattr(artwork.artist, 'artist_profile', None)
    return render(request, 'artwork_detail.html', {
        'artwork': artwork,
        'artist_profile': artist_profile,
    })


def artists(request):
    profiles = ArtistProfile.objects.select_related('user').all()
    return render(request, 'artists.html', {'profiles': profiles})


def artist_shop(request, pk):
    profile = get_object_or_404(ArtistProfile, pk=pk)
    artworks = Artwork.objects.filter(artist=profile.user, is_sold=False)
    return render(request, 'artist_shop.html', {
        'profile': profile,
        'artworks': artworks,
    })


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
