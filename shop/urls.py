from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    # URL for the main shop page (e.g., yoursite.com/shop/)
    path('', views.ProductListView.as_view(), name='product_list'),
    
    # URL for a single product's detail page (e.g., yoursite.com/shop/1/)
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
]
