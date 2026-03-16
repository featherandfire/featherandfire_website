
from django.contrib import admin
from django.urls import path


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.marketplace.urls")),
    path('accounts/', include('allauth.urls')),
]