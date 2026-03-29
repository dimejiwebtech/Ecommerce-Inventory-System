from django.urls import path
from . import views

app_name = 'accounts_ims'

urlpatterns = [
    path('wholesalers/', views.ims_wholesaler_list, name='ims_wholesaler_list'),
    path('wholesalers/<int:pk>/', views.ims_wholesaler_detail, name='ims_wholesaler_detail'),
    path('wholesalers/<int:pk>/approve/', views.ims_wholesaler_approve, name='ims_wholesaler_approve'),
    path('wholesalers/<int:pk>/reject/', views.ims_wholesaler_reject, name='ims_wholesaler_reject'),
    
    path('staff/', views.ims_staff_list, name='ims_staff_list'),
    path('staff/add/', views.ims_staff_add, name='ims_staff_add'),
    path('staff/<int:pk>/edit/', views.ims_staff_edit, name='ims_staff_edit'),
    path('staff/<int:pk>/delete/', views.ims_staff_delete, name='ims_staff_delete'),
]
