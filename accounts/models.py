import random
import re
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone



ROLE_CHOICES = [
    ('customer', 'Customer'),
    ('wholesaler', 'Wholesaler'),
    ('staff', 'Staff'),
    ('manager', 'Manager'),
    ('admin', 'Admin'),
]

STATUS_CHOICES = [
    ('active', 'Active'),
    ('inactive', 'Inactive'),
    ('on_leave', 'On Leave'),
]



class CustomUser(AbstractUser):

    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='customer'
    )
    phone = models.CharField(max_length=30, blank=True, null=True)
    is_email_verified = models.BooleanField(default=False)

    def is_verified_wholesaler(self):
        return (
            self.role == 'wholesaler'
            and hasattr(self, 'wholesaler_profile')
            and self.wholesaler_profile.is_verified
        )

    def is_ims_user(self):
        return self.role in ('staff', 'manager', 'admin')

    def __str__(self):
        return self.username




class WholesalerProfile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='wholesaler_profile'
    )
    whatsapp_number = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    applied_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        status = 'Verified' if self.is_verified else 'Pending'
        return f"{self.user.username} — {status}"




class Profile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='avatars/', blank=True, null=True
    )
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active'
    )

    def __str__(self):
        return f"{self.user.username} — Profile"



class Vendor(models.Model):

    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']



class Customer(models.Model):

    ref_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    def __str__(self):
        return self.full_name()

    class Meta:
        ordering = ['first_name']


class CustomerAddress(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='addresses'
    )
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=30)
    email = models.EmailField(blank=True, null=True)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Nigeria')
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.is_default:
            CustomerAddress.objects.filter(user=self.user).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} — {self.city}, {self.state}"

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = "Customer Addresses"


def _normalise_phone(raw):
    n = re.sub(r'[\s\-().+]', '', str(raw))
    if n.startswith('234'):
        n = '+' + n
    elif n.startswith('0'):
        n = '+234' + n[1:]
    elif not n.startswith('+'):
        n = '+234' + n
    return n


class WholesalerContact(models.Model):
    raw_number = models.CharField(max_length=30)
    normalised = models.CharField(max_length=30, unique=True)
    name = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.normalised = _normalise_phone(self.raw_number)
        super().save(*args, **kwargs)

    @classmethod
    def number_exists(cls, raw):
        return cls.objects.filter(normalised=_normalise_phone(raw)).exists()

    def __str__(self):
        return f"{self.name or 'Unknown'} — {self.normalised}"

    class Meta:
        ordering = ['name']


class EmailVerificationToken(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE,
        related_name='email_verification_token'
    )
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(hours=24)

    def __str__(self):
        return f"VerifyToken({self.user.username})"


OTP_INACTIVITY_DAYS = 30


class LoginOTP(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='login_otps'
    )
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    @classmethod
    def generate(cls, user):
        cls.objects.filter(user=user, is_used=False).delete()
        code = str(random.randint(100000, 999999))
        return cls.objects.create(user=user, code=code)

    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"OTP({self.user.username} — {'used' if self.is_used else 'active'})"

    class Meta:
        ordering = ['-created_at']


def otp_required_for(user):
    if user.last_login is None:
        return False
    days_since = (timezone.now() - user.last_login).days
    return days_since >= OTP_INACTIVITY_DAYS
