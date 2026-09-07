from decimal import Decimal, ROUND_HALF_UP

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class SellerProfile(models.Model):
    """Extra info attached to a User that represents a seller (shop)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='seller_profile')
    shop_name = models.CharField(max_length=150)
    address = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name


class CustomerProfile(models.Model):
    """Extra info attached to a User that represents a customer/shopper."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Product(models.Model):
    """A packed/surplus item a seller lists at a discounted rate."""

    CATEGORY_CHOICES = [
        ('bakery', 'Bakery'),
        ('grocery', 'Grocery / Packaged'),
        ('produce', 'Fruits & Vegetables'),
        ('dairy', 'Dairy'),
        ('meals', 'Ready Meals'),
        ('other', 'Other'),
    ]

    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    image = models.ImageField(upload_to='products/', blank=True, null=True)

    original_price = models.DecimalField(max_digits=8, decimal_places=2)
    discounted_price = models.DecimalField(max_digits=8, decimal_places=2)

    quantity_available = models.PositiveIntegerField(default=1)
    expiry_date = models.DateField(help_text="Best-before / use-by date")
    pickup_window = models.CharField(
        max_length=100, blank=True,
        help_text="e.g. 6:00 PM - 8:00 PM today"
    )

    # Commission is stored per-product (percent at time of listing) so it
    # never changes retroactively even if the platform default changes later.
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.seller.shop_name})"

    # ---- money helpers -----------------------------------------------
    def commission_amount(self):
        """Commission taken by the platform on ONE unit. Seller-only info."""
        amount = (self.discounted_price * self.commission_percent) / Decimal('100')
        return amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def seller_earning_per_unit(self):
        """What the seller actually receives per unit after commission."""
        return self.discounted_price - self.commission_amount()

    def discount_percent(self):
        if self.original_price and self.original_price > 0:
            pct = (1 - (self.discounted_price / self.original_price)) * 100
            return int(pct)
        return 0

    # ---- expiry helpers -------------------------------------------------
    def days_to_expiry(self):
        return (self.expiry_date - timezone.localdate()).days

    def is_near_expiry(self):
        return 0 <= self.days_to_expiry() <= 2

    def is_expired(self):
        return self.days_to_expiry() < 0

    def is_available(self):
        return self.is_active and self.quantity_available > 0 and not self.is_expired()


class Order(models.Model):
    STATUS_CHOICES = [
        ('placed', 'Placed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, related_name='sales')

    quantity = models.PositiveIntegerField(default=1)

    # Snapshots taken at order time so later price/commission edits don't
    # rewrite order history.
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    commission_amount_total = models.DecimalField(max_digits=8, decimal_places=2)
    seller_earning_total = models.DecimalField(max_digits=8, decimal_places=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    # The customer MUST tick this box acknowledging the expiry-risk
    # disclaimer before an order can be created.
    disclaimer_accepted = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='placed')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.product.name} x{self.quantity}"
