from django.db import models
from django.conf import settings
from orders.models import OrderItem

class Stockpile(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stockpiles'
    )
    order_item = models.OneToOneField(
        OrderItem, on_delete=models.CASCADE, related_name='stockpile'
    )
    stored_since = models.DateTimeField(auto_now_add=True)
    is_released = models.BooleanField(default=False)
    released_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Stockpile: {self.order_item.jewellery.name} for {self.user.username}"

    @property
    def days_stored(self):
        from django.utils import timezone
        end_date = self.released_at or timezone.now()
        delta = end_date - self.stored_since
        return delta.days

    @property
    def current_fee(self):
        """₦200/day after 30 days free."""
        days = self.days_stored
        if days <= 30:
            return 0
        return (days - 30) * 200

class StockpileFeeLog(models.Model):
    stockpile = models.ForeignKey(
        Stockpile, on_delete=models.CASCADE, related_name='fee_logs'
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_accrued = models.DateField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fee: ₦{self.amount} on {self.date_accrued}"
