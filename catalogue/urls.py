from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    # Products
    path('products/', views.ims_product_list, name='ims_product_list'),
    path('products/add/', views.ims_product_add, name='ims_product_add'),
    path('products/edit/<int:pk>/', views.ims_product_edit, name='ims_product_edit'),
    path('products/delete/<int:pk>/', views.ims_product_delete, name='ims_product_delete'),

    # Categories
    path('categories/', views.ims_category_list, name='ims_category_list'),
    path('categories/add/', views.ims_category_add, name='ims_category_add'),
    path('categories/<int:pk>/edit/', views.ims_category_edit, name='ims_category_edit'),
    path('categories/<int:pk>/delete/', views.ims_category_delete, name='ims_category_delete'),

    # Collections
    path('collections/', views.ims_collection_list, name='ims_collection_list'),
    path('collections/add/', views.ims_collection_add, name='ims_collection_add'),
    path('collections/<int:pk>/edit/', views.ims_collection_edit, name='ims_collection_edit'),
    path('collections/<int:pk>/delete/', views.ims_collection_delete, name='ims_collection_delete'),

    # Vendors
    path('vendors/', views.ims_vendor_list, name='ims_vendor_list'),
    path('vendors/add/', views.ims_vendor_add, name='ims_vendor_add'),
    path('vendors/edit/<int:pk>/', views.ims_vendor_edit, name='ims_vendor_edit'),

    # Purchase Orders
    path('purchase-orders/', views.ims_po_list, name='ims_po_list'),
    path('purchase-orders/add/', views.ims_po_add, name='ims_po_add'),
    path('purchase-orders/edit/<int:pk>/', views.ims_po_edit, name='ims_po_edit'),
    path('purchase-orders/receive/<int:pk>/', views.ims_po_receive, name='ims_po_receive'),
    
    # Stock Movements
    path('stock-movements/', views.ims_stock_movements, name='ims_stock_movements'),

    # Variations & Sizes
    path('variants/', views.ims_variant_list, name='ims_variant_list'),
    path('variants/add/', views.ims_variant_add, name='ims_variant_add'),
    path('variants/edit/<int:pk>/', views.ims_variant_edit, name='ims_variant_edit'),
    path('variants/delete/<int:pk>/', views.ims_variant_delete, name='ims_variant_delete'),

    # Announcements
    path('announcements/', views.ims_announcement_list, name='ims_announcement_list'),
    path('announcements/add/', views.ims_announcement_add, name='ims_announcement_add'),
    path('announcements/<int:pk>/edit/', views.ims_announcement_edit, name='ims_announcement_edit'),
    path('announcements/<int:pk>/delete/', views.ims_announcement_delete, name='ims_announcement_delete'),
]
