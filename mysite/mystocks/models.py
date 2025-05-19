from django.db import models

# Create your models here.
from django.db import models

class StockPrice(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open = models.FloatField()
    high = models.FloatField()
    low = models.FloatField()
    close = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('symbol', 'date')
        ordering = ['-date']
