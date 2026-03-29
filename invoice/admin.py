from django.contrib import admin
from invoice.models import Invoice


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'customer_name', 'customer_email', 'grand_total', 'issued_at')
    list_filter = ('issued_at',)
    search_fields = ('invoice_number', 'customer_name', 'customer_email')
    readonly_fields = ('invoice_number', 'ref_id', 'issued_at')
