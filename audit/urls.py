from django.urls import path
from . import views

urlpatterns = [
    path('', views.ims_activity_history, name='ims_activity_history'),
]
