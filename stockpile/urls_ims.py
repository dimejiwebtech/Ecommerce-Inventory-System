from django.urls import path
from . import views

app_name = 'stockpile_ims'

urlpatterns = [
    path('', views.ims_stockpile_list, name='ims_stockpile_list'),
]
