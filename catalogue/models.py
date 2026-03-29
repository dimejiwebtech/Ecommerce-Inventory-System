import uuid

from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    banner = models.ImageField(upload_to='collections/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']





class Jewellery(models.Model):
    STOCK_STATUS = [
        ('in_stock', 'In Stock'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
    ]

    # BigInt PK (default). UUID for public URLs.
    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True, max_length=220)
    description = models.TextField()
    sku = models.CharField(max_length=50, unique=True)
    weight_grams = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )

    # Pricing
    retail_price = models.DecimalField(max_digits=12, decimal_places=2)
    wholesale_price = models.DecimalField(max_digits=12, decimal_places=2)

    # Inventory
    stock = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)

    # Relations
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name='jewellery'
    )
    collection = models.ForeignKey(
        Collection, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='jewellery'
    )

    # Flags
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def stock_status(self):
        if self.stock == 0:
            return 'out_of_stock'
        if self.stock <= self.low_stock_threshold:
            return 'low_stock'
        return 'in_stock'

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    def get_price_for_user(self, user):
        """Return the right price based on user's verified wholesaler status."""
        if (
            user.is_authenticated
            and user.role == 'wholesaler'
            and hasattr(user, 'wholesaler_profile')
            and user.wholesaler_profile.is_verified
        ):
            return self.wholesale_price
        return self.retail_price

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Jewellery'
        ordering = ['name']


class JewelleryVariant(models.Model):
    """Handles size and color variations for a given jewellery piece."""
    jewellery = models.ForeignKey(Jewellery, on_delete=models.CASCADE, related_name='variants')
    size = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., '7', '18 inch'")
    color = models.CharField(max_length=50, blank=True, null=True, help_text="e.g., 'Rose Gold'")
    stock = models.PositiveIntegerField(default=0)
    image = models.ForeignKey('JewelleryImage', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        unique_together = ('jewellery', 'size', 'color')

    def __str__(self):
        parts = []
        if self.color: parts.append(self.color)
        if self.size: parts.append(f"Size {self.size}")
        label = " - ".join(parts) if parts else "Standard"
        return f"{self.jewellery.name} ({label})"


class JewelleryImage(models.Model):
    jewellery = models.ForeignKey(
        Jewellery, on_delete=models.CASCADE, related_name='images'
    )
    image = models.ImageField(upload_to='jewellery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.jewellery.name} — image {self.order}"

    class Meta:
        ordering = ['order']


class StockMovement(models.Model):
    REASON_CHOICES = [
        ('purchase', 'Purchase Order'),
        ('sale', 'Sale'),
        ('pos_sale', 'POS Sale'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Return'),
    ]

    jewellery = models.ForeignKey(
        Jewellery, on_delete=models.CASCADE, related_name='stock_movements'
    )
    change = models.IntegerField(help_text='Positive = stock in, Negative = stock out')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    note = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        'accounts.CustomUser', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='stock_movements'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        direction = '+' if self.change > 0 else ''
        return f"{self.jewellery.name} {direction}{self.change} ({self.get_reason_display()})"

    class Meta:
        ordering = ['-created_at']


class Announcement(models.Model):
    text = models.CharField(max_length=500)
    link = models.URLField(blank=True, null=True)
    link_label = models.CharField(max_length=50, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:60]

    class Meta:
        ordering = ['-created_at']


class Vendor(models.Model):
    name = models.CharField(max_length=200)
    contact_person = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('ordered', 'Ordered'),
        ('received', 'Received'),
        ('cancelled', 'Cancelled'),
    ]

    po_number = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchase_orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    order_date = models.DateField(default=timezone.now)
    received_date = models.DateField(blank=True, null=True)
    
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    notes = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.po_number

    class Meta:
        ordering = ['-created_at']


class PurchaseOrderItem(models.Model):
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='items')
    jewellery = models.ForeignKey(Jewellery, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    
    @property
    def total_price(self):
        return self.quantity * self.unit_cost

    def __str__(self):
        return f"{self.purchase_order.po_number} - {self.jewellery.name}"
