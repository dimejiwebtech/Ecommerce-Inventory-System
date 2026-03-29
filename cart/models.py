import uuid

from django.conf import settings
from django.db import models

from catalogue.models import Jewellery

class Cart(models.Model):
    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='cart'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def total(self):
        return sum(item.line_total() for item in self.items.all())

    def item_count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Cart {self.ref_id}"

    class Meta:
        ordering = ['-updated_at']


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    jewellery = models.ForeignKey(Jewellery, on_delete=models.CASCADE)
    variant = models.ForeignKey('catalogue.JewelleryVariant', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def unit_price(self):
        user = self.cart.user
        if (
            user
            and user.role == 'wholesaler'
            and hasattr(user, 'wholesaler_profile')
            and user.wholesaler_profile.is_verified
        ):
            return self.jewellery.wholesale_price
        return self.jewellery.retail_price

    def line_total(self):
        return self.unit_price() * self.quantity

    def __str__(self):
        v = f" ({self.variant.size or ''} {self.variant.color or ''})".strip() if self.variant else ""
        return f"{self.quantity}x {self.jewellery.name}{v}"

    class Meta:
        unique_together = ('cart', 'jewellery', 'variant')


class Wishlist(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wishlist'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s wishlist"


class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, on_delete=models.CASCADE, related_name='items')
    jewellery = models.ForeignKey(Jewellery, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.jewellery.name

    class Meta:
        unique_together = ('wishlist', 'jewellery')
