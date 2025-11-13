from django.db import models

# Create your models here.
# In shop/models.py

from django.conf import settings

class Product(models.Model):
    # The name of your digital product (e.g., "AI Art: Raipur Cityscapes Pack")
    title = models.CharField(max_length=200)

    # A detailed description of what the user is buying
    description = models.TextField()

    # The price. We use DecimalField for money to avoid rounding errors.
    price = models.DecimalField(max_digits=8, decimal_places=2)

    # A preview image that will be shown in the shop (stored on S3)
    preview_image = models.ImageField(upload_to='product_previews/')

    # The actual downloadable file the user gets after purchase (stored on S3)
    digital_file = models.FileField(upload_to='digital_products/')

    # The user who created this product (you, the admin)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Automatically records when the product was added
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This ensures your newest products always appear first
        ordering = ['-created_at']

    def __str__(self):
        return self.title
