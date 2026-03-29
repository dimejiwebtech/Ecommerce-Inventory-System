from django.urls import path

from orders import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('confirm/<uuid:ref_id>/', views.order_confirm, name='order_confirm'),
    path('my-orders/', views.order_list, name='order_list'),
    path('my-orders/<uuid:ref_id>/', views.order_detail, name='order_detail'),
    path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
]
