from django.contrib import admin

from bills.models import Bill


@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('institution_name', 'amount', 'status', 'due_date', 'created_at')
    list_filter = ('status',)
    search_fields = ('institution_name', 'email')
