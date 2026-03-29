from django.urls import path
from . import views

app_name = 'orders_ims'

urlpatterns = [
    path('', views.ims_order_list, name='ims_order_list'),
    path('<uuid:ref_id>/', views.ims_order_detail, name='ims_order_detail'),
    
    # Shipments
    path('shipments/', views.ims_shipment_list, name='ims_shipment_list'),
    path('shipments/add/<uuid:ref_id>/', views.ims_shipment_add, name='ims_shipment_add'),
    path('shipments/edit/<int:pk>/', views.ims_shipment_edit, name='ims_shipment_edit'),
]
