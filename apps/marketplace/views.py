import logging
import stripe
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)
from .models import Artwork, Order
from .forms import SellerApplicationForm
from apps.users.models import ArtistProfile

stripe.api_key = settings.STRIPE_SECRET_KEY


def home(request):
    featured_artists = ArtistProfile.objects.filter(is_featured=True).select_related('user')[:3]
    artwork_count = Artwork.objects.count()
    artist_count = ArtistProfile.objects.count()
    hero_artworks = Artwork.objects.exclude(image='').order_by('?')[:12]
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
    artist_profile = getattr(artwork.artist, 'artist_profile', None)
    artist_name = artist_profile.display_name if artist_profile else artwork.artist.email
    product_description = f'{artwork.get_medium_display()} by {artist_name}'
    if artwork.description:
        product_description += f' — {artwork.description[:200]}'

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'unit_amount': int(artwork.price * 100),
                'product_data': {
                    'name': artwork.title,
                    'description': product_description,
                },
            },
            'quantity': 1,
        }],
        mode='payment',
        shipping_address_collection={'allowed_countries': ['US', 'CA']},
        success_url=request.build_absolute_uri(f'/order/success/?session_id={{CHECKOUT_SESSION_ID}}'),
        cancel_url=request.build_absolute_uri(f'/artwork/{pk}/'),
        metadata={'artwork_id': pk, 'artist': artist_name},
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

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        payment_status = session.get('payment_status')
        artwork_id = session.get('metadata', {}).get('artwork_id')
        print(f'Webhook received: payment_status={payment_status}, artwork_id={artwork_id}, session_id={session["id"]}')

        print(f'DEBUG: payment_status={payment_status!r}, artwork_id={artwork_id!r}')
        if payment_status == 'paid' and artwork_id:
            try:
                artwork = Artwork.objects.get(pk=artwork_id)
                print(f'DEBUG: artwork found: {artwork}')
                try:
                    full_session = stripe.checkout.Session.retrieve(session['id'])
                except Exception as e:
                    print(f'STRIPE RETRIEVE ERROR: {e}')
                    full_session = session
                collected = full_session.get('collected_information') or {}
                shipping = collected.get('shipping_details') or full_session.get('shipping_details') or full_session.get('shipping') or {}
                print(f'DEBUG shipping: {shipping}')
                shipping_address_obj = shipping.get('address', {})
                shipping_address = ', '.join(filter(None, [
                    shipping_address_obj.get('line1', ''),
                    shipping_address_obj.get('line2', ''),
                    shipping_address_obj.get('city', ''),
                    shipping_address_obj.get('state', ''),
                    shipping_address_obj.get('postal_code', ''),
                    shipping_address_obj.get('country', ''),
                ]))
                order, created = Order.objects.get_or_create(
                    stripe_session_id=session['id'],
                    defaults={
                        'artwork': artwork,
                        'buyer_email': session.get('customer_details', {}).get('email', ''),
                        'amount': artwork.price,
                        'paid': True,
                        'shipping_name': shipping.get('name', ''),
                        'shipping_address': shipping_address,
                    }
                )
                if not created and not order.shipping_address:
                    order.shipping_name = shipping.get('name', '')
                    order.shipping_address = shipping_address
                    order.save()
                artwork.is_sold = True
                artwork.save()
            except Artwork.DoesNotExist:
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
    artworks = Artwork.objects.filter(artist=profile.user)
    return render(request, 'artist_shop.html', {
        'profile': profile,
        'artworks': artworks,
    })


@login_required
def dashboard(request):
    if not request.user.is_seller:
        return HttpResponseForbidden()
    profile = getattr(request.user, 'artist_profile', None)
    artworks = Artwork.objects.filter(artist=request.user).order_by('-created_at')
    sold = artworks.filter(is_sold=True)
    total_sales = sum(
        order.amount for order in Order.objects.filter(artwork__artist=request.user, paid=True)
    )
    return render(request, 'dashboard.html', {
        'profile': profile,
        'artworks': artworks,
        'sold_count': sold.count(),
        'available_count': artworks.filter(is_sold=False).count(),
        'total_sales': total_sales,
    })


def gallery(request):
    artworks = Artwork.objects.select_related('artist__artist_profile')

    medium = request.GET.get('medium')
    if medium:
        artworks = artworks.filter(medium=medium)

    context = {
        'artworks': artworks,
        'medium_choices': Artwork.MEDIUM_CHOICES,
        'selected_medium': medium,
    }
    return render(request, 'gallery.html', context)
