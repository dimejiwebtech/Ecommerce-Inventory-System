from django.urls import path
from . import views

app_name = 'pos'

urlpatterns = [
    path('', views.ims_pos, name='ims_pos'),
    path('api/search/', views.ims_pos_search, name='ims_pos_search'),
    path('api/checkout/', views.ims_pos_checkout, name='ims_pos_checkout'),
]
