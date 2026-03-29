from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from .views import tinymce_upload
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/', tinymce_upload),

    # Shop (frontend)
    path('', include('shop.urls')),

    # Auth & Accounts
    path('accounts/', include('accounts.urls', namespace='accounts')),

    # Customer-facing
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('stockpile/', include('stockpile.urls')),

    # IMS back-office
    path('ims/', include([
        path('', include('reports.urls')),
        path('pos/', include('pos.urls')),
        path('catalogue/', include('catalogue.urls')),
        path('accounts/', include('accounts.urls_ims', namespace='accounts_ims')),
        path('orders/', include('orders.urls_ims', namespace='orders_ims')),
        path('stockpile/', include('stockpile.urls_ims', namespace='stockpile_ims')),
        path('invoice/', include('invoice.urls')),
        path('bills/', include('bills.urls')),
        path('reviews/', include('reviews.urls')),
        path('history/', include('audit.urls')),
    ])),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
