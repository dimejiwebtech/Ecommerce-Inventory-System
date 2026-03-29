from django.urls import path
from . import views

app_name = 'stockpile'

urlpatterns = [
    path('', views.stockpile_list, name='stockpile_list'),
]
