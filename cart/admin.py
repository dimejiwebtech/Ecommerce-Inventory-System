from django.contrib import admin

from cart.models import Cart, CartItem, Wishlist, WishlistItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ('line_total',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('ref_id', 'user', 'session_key', 'item_count', 'total', 'updated_at')
    inlines = [CartItemInline]
    readonly_fields = ('ref_id',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
