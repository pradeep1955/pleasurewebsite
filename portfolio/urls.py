# In portfolio/urls.py

from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Main dashboard view
    path('', views.portfolio_dashboard, name='dashboard'),
    
    # URLs for managing holdings
    path('add/', views.add_holding, name='add_holding'),
    path('<int:pk>/edit/', views.edit_holding, name='edit_holding'),
    path('<int:pk>/delete/', views.delete_holding, name='delete_holding'),
]
