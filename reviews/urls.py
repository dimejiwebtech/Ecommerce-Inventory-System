from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('', views.ims_review_list, name='ims_review_list'),
    path('approve/<int:pk>/', views.ims_review_approve, name='ims_review_approve'),
    path('delete/<int:pk>/', views.ims_review_delete, name='ims_review_delete'),
]
