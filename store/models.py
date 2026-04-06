from django.db import models
from django.contrib.auth.models import User

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Pain Relief', 'Pain Relief'),
        ('Antibiotics', 'Antibiotics'),
        ('Supplements', 'Supplements'),
        ('First Aid', 'First Aid'),
        ('Malaria', 'Malaria'),
        ('Sexual Health', 'Sexual Health'),
    )

    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Pain Relief')
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='medicines/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    
    # THIS is the correct name format for a Product
    def __str__(self):
        return self.name


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default='Completed')
    created_at = models.DateTimeField(auto_now_add=True)

    # THIS is the correct name format for an Order
    def __str__(self):
        return f"Order #{self.id} - GHS {self.total_amount}"