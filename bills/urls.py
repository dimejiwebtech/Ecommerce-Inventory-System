from django.urls import path
from . import views

app_name = 'bills'

urlpatterns = [
    path('', views.ims_bill_list, name='ims_bill_list'),
    path('add/', views.ims_bill_add, name='ims_bill_add'),
    path('<int:pk>/', views.ims_bill_detail, name='ims_bill_detail'),
    path('<int:pk>/edit/', views.ims_bill_edit, name='ims_bill_edit'),
    path('<int:pk>/delete/', views.ims_bill_delete, name='ims_bill_delete'),
]
