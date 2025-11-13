from django.db import models

# Create your models here.
# In portfolio/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone

class Holding(models.Model):
    # Link each holding to a specific user
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # The stock ticker symbol (e.g., 'SBIN.BO', 'RELIANCE.NS')
    # Use max_length=20 to accommodate longer symbols if needed
    symbol = models.CharField(max_length=20)

    # Number of shares owned. Using DecimalField for potential fractional shares.
    quantity = models.DecimalField(max_digits=10, decimal_places=2)

    # The price paid per share at the time of purchase
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)

    # The date the shares were purchased
    purchase_date = models.DateField(default=timezone.now)

    class Meta:
        # Ensures a user cannot have two entries for the same stock symbol
        # You might remove this if you want to track multiple purchases separately
        unique_together = ('user', 'symbol')
        # Order holdings alphabetically by symbol by default
        ordering = ['symbol']

    def __str__(self):
        # A clear representation in the admin panel
        return f"{self.user.username} - {self.quantity} shares of {self.symbol}"
