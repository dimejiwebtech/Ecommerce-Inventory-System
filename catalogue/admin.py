from django.contrib import admin
from django.db import models
from tinymce.widgets import TinyMCE

from catalogue.models import (
    Announcement, Category, Collection, Jewellery, JewelleryImage,
    JewelleryVariant, PurchaseOrder, PurchaseOrderItem, StockMovement,
    Vendor
)


class JewelleryImageInline(admin.TabularInline):
    model = JewelleryImage
    extra = 1

class JewelleryVariantInline(admin.TabularInline):
    model = JewelleryVariant
    extra = 0

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 0

@admin.register(Jewellery)
class JewelleryAdmin(admin.ModelAdmin):
    list_display = (
        'sku', 'name', 'category', 'collection',
        'retail_price', 'wholesale_price', 'stock', 'is_active'
    )
    list_filter = ('category', 'collection', 'is_featured', 'is_active')
    search_fields = ('name', 'sku')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [JewelleryVariantInline, JewelleryImageInline]
    readonly_fields = ('ref_id', 'created_at', 'updated_at')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE},
    }

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_featured', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_person', 'email', 'phone')
    search_fields = ('name', 'contact_person')

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_number', 'vendor', 'status', 'order_date', 'total_amount')
    list_filter = ('status', 'vendor')
    search_fields = ('po_number',)
    inlines = [PurchaseOrderItemInline]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('jewellery', 'change', 'reason', 'user', 'created_at')
    list_filter = ('reason',)
    readonly_fields = ('created_at',)

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('text', 'is_active', 'created_at')
    list_filter = ('is_active',)

