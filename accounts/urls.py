from django.urls import path

from accounts import views

from orders import views as order_views
from stockpile import views as stockpile_views
from cart import views as cart_views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('profile/', views.profile, name='profile'),
    path('addresses/', views.address_list, name='address_list'),
    path('addresses/add/', views.address_add, name='address_add'),
    path('addresses/delete/<int:pk>/', views.address_delete, name='address_delete'),

    # Consolidated Sidebar URLs
    path('orders/', order_views.order_list, name='order_list'),
    path('orders/<uuid:ref_id>/', order_views.order_detail, name='order_detail'),
    path('stockpile/', stockpile_views.stockpile_list, name='stockpile_list'),
    path('wishlist/', cart_views.wishlist_page, name='wishlist'),

    # Email verification
    path('verify-email/sent/', views.verify_email_sent, name='verify_email_sent'),
    path('verify-email/<uuid:token>/', views.verify_email, name='verify_email'),
    path('verify-email/resend/', views.resend_verification, name='resend_verification'),

    # OTP
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
]
