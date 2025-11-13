from django.shortcuts import render

# Create your views here.
# In shop/views.py

from django.views import generic
from .models import Product

class ProductListView(generic.ListView):
    """
    Displays a list of all products.
    """
    model = Product
    template_name = 'shop/product_list.html'
    context_object_name = 'products'  # Use 'products' as the variable name in the template

class ProductDetailView(generic.DetailView):
    """
    Displays the details for a single product.
    """
    model = Product
    template_name = 'shop/product_detail.html'
    context_object_name = 'product'
