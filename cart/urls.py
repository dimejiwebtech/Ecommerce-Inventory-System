from django.urls import path

from cart import views

urlpatterns = [
    path('', views.cart_detail, name='cart_detail'),
    # POST-body form submissions from product cards / product detail
    path('add/', views.cart_add, name='cart_add'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('wishlist/', views.wishlist_page, name='wishlist'),
    path('wishlist/toggle/', views.wishlist_toggle, name='wishlist_toggle'),
    # legacy pk-in-path (kept for back-compat)
    path('add/<int:jewellery_id>/', views.cart_add_pk, name='add_to_cart'),
    path('wishlist/toggle/<int:jewellery_id>/', views.wishlist_toggle_pk, name='toggle_wishlist'),
]
