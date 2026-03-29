import uuid

from django.db import models


# ─── Invoice (linked to Order or POS Sale) ────────────────────────────────────

class Invoice(models.Model):
    """Invoice generated for an online order or offline POS sale."""

    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    invoice_number = models.CharField(max_length=20, unique=True, editable=False)

    # Generic: either an online order ID or a POS sale ID, stored as plain int
    order_ref = models.CharField(max_length=50, blank=True, null=True)
    sale_ref = models.CharField(max_length=50, blank=True, null=True)

    customer_name = models.CharField(max_length=100)
    customer_email = models.EmailField(blank=True, null=True)
    customer_phone = models.CharField(max_length=30, blank=True, null=True)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    shipping = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    issued_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.invoice_number:
            last = Invoice.objects.order_by('-id').first()
            next_num = (last.id + 1) if last else 1
            self.invoice_number = f"INV-{next_num:06d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.invoice_number

    class Meta:
        ordering = ['-issued_at']
