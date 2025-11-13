from django.urls import path
from . import views
from myapp.views import contact_list, invited_guests, edit_guest
from myapp.views import contact_list, invited_contacts, not_invited_contacts, invited_guests, edit_guest
urlpatterns = [
    path('', views.contact_list, name='contact_list'),
    path('invited/', views.invited_contacts, name='invited_contacts'),
    path('not-invited/', views.not_invited_contacts, name='not_invited_contacts'),
    path('whatsapp-helper/', views.whatsapp_helper_view, name='whatsapp_helper'),
    path('create/', views.contact_create, name='contact_create'),
    path('<int:pk>/edit/', views.contact_edit, name='contact_edit'),
    path('<int:pk>/delete/', views.contact_delete, name='contact_delete'),
    path('guests/', invited_guests, name='invited_guests'),
    path('guests/edit/<int:contact_id>/', edit_guest, name='edit_guest'),
    
    # Hotel URLs
#    path('hotels/', hotel_list, name='hotel_list'),
#    path('hotels/add/', hotel_create, name='hotel_create'),
#    path('hotels/<int:pk>/edit/', hotel_edit, name='hotel_edit'),
#    path('hotels/<int:pk>/delete/', hotel_delete, name='hotel_delete'),
    path('hotels/', views.hotel_list, name='hotel_list'),
    path('hotels/new/', views.hotel_create, name='hotel_create'),
    path('hotels/<int:pk>/edit/', views.hotel_update, name='hotel_update'),
    path('hotels/<int:pk>/delete/', views.hotel_delete, name='hotel_delete'),
    path('export/', views.export_to_excel, name='export_to_excel'),
    path('visitor-chart/', views.visitor_chart, name='visitor_chart'),


]
