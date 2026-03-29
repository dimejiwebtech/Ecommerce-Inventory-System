from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('dashboard/', views.ims_dashboard, name='ims_dashboard'),
    path('api/sales-chart/', views.ims_sales_chart_data, name='ims_sales_chart_data'),
    path('partials/notifications/', views.ims_notifications, name='ims_notifications'),


    path('reports/sales/', views.ims_sales_report, name='ims_sales_report'),
    path('reports/inventory/', views.ims_inventory_report, name='ims_inventory_report'),
    path('reports/customers/', views.ims_customer_report, name='ims_customer_report'),
]
