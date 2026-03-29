from django.db import models
from django.conf import settings
from catalogue.models import Jewellery, JewelleryVariant

class Sale(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('pos', 'POS (Card)'),
        ('transfer', 'Bank Transfer'),
    ]

    staff = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='pos_sales')
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='cash')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional customer info for receipt
    customer_name = models.CharField(max_length=255, blank=True, null=True)
    customer_phone = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Sale #{self.id} - {self.total_amount}"

class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    jewellery = models.ForeignKey(Jewellery, on_delete=models.CASCADE)
    variant = models.ForeignKey(JewelleryVariant, on_delete=models.SET_NULL, null=True, blank=True)
    
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.jewellery.name}"
