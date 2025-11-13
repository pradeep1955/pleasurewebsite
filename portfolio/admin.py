from django.contrib import admin

# Register your models here.
# In portfolio/admin.py

from django.contrib import admin
from .models import Holding

class HoldingAdmin(admin.ModelAdmin):
    # Display these fields in the admin list view
    list_display = ('user', 'symbol', 'quantity', 'purchase_price', 'purchase_date')
    # Allow filtering by user and purchase date
    list_filter = ('user', 'purchase_date')
    # Allow searching by symbol
    search_fields = ('symbol',)
    # Order by symbol by default in the admin
    ordering = ('symbol',)

admin.site.register(Holding, HoldingAdmin)
