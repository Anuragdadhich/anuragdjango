from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profile_image = models.ImageField(upload_to='profile_images/', default='default.jpg')
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username

class shopping(models.Model):
    name = models.CharField(max_length=200)  # Shoe name
    description = models.TextField()  # Shoe description
    category = models.CharField(max_length=300, default=3)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Shoe price
    sizes = models.CharField(max_length=255, blank=True, null=True) # Comma-separated sizes
    colors = models.CharField(max_length=255, blank=True, null=True) # Available colors (e.g., ["Red", "Black", "Blue"])
    image = models.ImageField(upload_to='images/')  # Shoe image
    stock = models.PositiveIntegerField(default=0)  # Stock count
    is_active = models.BooleanField(default=True)  # Whether the product is active/available
    is_featured_carousel = models.BooleanField(default=False) # for the top carousel.
    carousel_description = models.TextField(blank=True, null=True)
    exclusive_start_date = models.DateField(blank=True, null=True)
    exclusive_end_date = models.DateField(blank=True, null=True)
    def __str__(self):
        return f"{self.name}"
class ShoeSize(models.Model):
    
    size = models.CharField(max_length=5)  # Example: "US 8", "EU 41", "UK 6"

    def __str__(self):
        return f"{self.shoe.name} - {self.size}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=50, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def update_total_price(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.order_items.all())
        self.save()

    def __str__(self):
        return f"Order #{self.id} for {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(shopping, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class Category(models.Model):
    name = models.CharField(max_length=100, default=3,)

    def __str__(self):
        return self.name
