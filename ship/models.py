from django.contrib.auth.models import User
from django.db import models
import uuid
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profile_image = models.ImageField(upload_to='profile_image/', default='default.jpg')
    name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    bio = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    def save(self, *args, **kwargs):
        # Open the image
        img = Image.open(self.profile_image)
        
        # Convert to RGB (for compatibility)
        img = img.convert("RGB")

        # Resize the image (optional)
        img.thumbnail((600, 600))  # Adjust size as needed

        # Compress and save as WebP
        img_io = BytesIO()
        img.save(img_io, format="WEBP", quality=85)  # Adjust quality (50-80 recommended)

        # Create a new Django image file
        self.profile_image = InMemoryUploadedFile(
            img_io,
            "ImageField",
            f"{self.profile_image.name.split('.')[0]}.webp",
            "image/webp",
            sys.getsizeof(img_io),
            None
        )

        super().save(*args, **kwargs)
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
    recommended_shoes = models.ManyToManyField('self', blank=True)  
    def save(self, *args, **kwargs):
        # Open the uploaded image
        img = Image.open(self.image)

        # Convert to RGB (to prevent transparency issues)
        img = img.convert("RGB")

        # Resize while maintaining aspect ratio
        max_size = (600, 600)  # Increase size if needed
        img.thumbnail(max_size)

        # Compress and save with higher quality
        img_io = BytesIO()
        img.save(img_io, format="WEBP", quality=85)  # Increase quality (70-90 for balance)

        # Replace the uploaded file with the compressed version
        self.profile_image = InMemoryUploadedFile(
            img_io,
            "ImageField",
            f"{self.image.name.split('.')[0]}.webp",
            "image/webp",
            sys.getsizeof(img_io),
            None
        )

        super().save(*args, **kwargs)  # Save the model instance
    
    def __str__(self):
        return f"{self.name}"
    def discounted_price(self):
        """Calculate the price after discount"""
        if self.discount > 0:
            return round(self.price - (self.price * self.discount / 100), 2)
        return self.price  # Return original price if no discount

class ShoeSize(models.Model):
    
    size = models.CharField(max_length=5)  # Example: "US 8", "EU 41", "UK 6"

    def __str__(self):
        return f"{self.shoe.name} - {self.size}"

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=[
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered")
    ], default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=[
        ("Pending (COD)", "Pending (COD)"),
        ("Paid", "Paid"),
        ("Failed", "Failed")
    ], default="Pending (COD)")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)

    def update_total_price(self):
        self.total_price = sum(item.product.price * item.quantity for item in self.order_items.all())
        self.save()

    def __str__(self):
        return f"Order #{self.id} for {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name="order_items", on_delete=models.CASCADE)
    product = models.ForeignKey(shopping, on_delete=models.CASCADE)
    sizes = models.CharField(max_length=255, blank=True, null=True) # Comma-separated sizes
    colors = models.CharField(max_length=255, blank=True, null=True) 
    sizes = models.CharField(max_length=10)  # Store selected size
    colors = models.CharField(max_length=20)  # Store selected color
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"

class Category(models.Model):
    name = models.CharField(max_length=100, default=3,)

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # ✅ User ko link karna zaroori hai
    product = models.ForeignKey(shopping, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.quantity})"
