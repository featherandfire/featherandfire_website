from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('apply/', views.apply, name='apply'),
    path('artwork/<int:pk>/', views.artwork_detail, name='artwork_detail'),
    path('artwork/<int:pk>/checkout/', views.checkout, name='checkout'),
    path('artists/<int:pk>/', views.artist_shop, name='artist_shop'),
    path('order/success/', views.order_success, name='order_success'),
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
]
