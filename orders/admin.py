from django.contrib import admin

from orders.models import Coupon, Order, OrderItem, OrderStatusHistory, ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('line_total',)


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ('changed_at',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'status', 'grand_total', 'placed_at')
    list_filter = ('status', 'placed_at')
    search_fields = ('order_number', 'customer_name', 'customer_email')
    readonly_fields = ('ref_id', 'order_number', 'placed_at', 'updated_at')
    inlines = [OrderItemInline, ShippingAddressInline, OrderStatusHistoryInline]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'times_used', 'valid_from', 'valid_to', 'is_active')
    list_filter = ('discount_type', 'is_active')
