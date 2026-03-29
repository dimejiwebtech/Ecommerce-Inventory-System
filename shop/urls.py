from django.urls import path

from shop import views

urlpatterns = [
    path('', views.home, name='home'),
    path('shop/', views.shop_list, name='shop_list'),
    path('shop/<slug:slug>/', views.product_detail, name='product_detail'),
    path('collections/', views.collections, name='collections'),
    path('collections/<slug:slug>/', views.collection_detail, name='collection_detail'),
    path('search/', views.search, name='search'),
    path('newsletter/signup/', views.newsletter_signup, name='newsletter_signup'),
    path('announcements/banner/', views.announcement_banner, name='announcement_banner'),
]
