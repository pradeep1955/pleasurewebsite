# Django Core Imports
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
from django.db.models.functions import TruncDate

# Standard Library Imports
import json
import urllib.parse
from io import BytesIO
import base64

# Third-Party Imports
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Your App's Models and Forms
from .models import Contact, Hotel, Visitor, DailyMessage
from .forms import ContactForm, HotelForm

# ==============================================================================
# WHATSAPP MESSAGE HELPER VIEW
# ==============================================================================

@login_required
def whatsapp_helper_view(request):
    """
    Displays a helper page to send pre-written WhatsApp messages to contacts.
    This page is restricted to superusers only.
    """
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized: This page is for administrators only.", status=403)

    today = timezone.now().date()
    daily_message_obj = DailyMessage.objects.filter(created_date=today).first()
    contacts = Contact.objects.all().order_by('fname')

    encoded_message = ""
    if daily_message_obj:
        encoded_message = urllib.parse.quote(daily_message_obj.message_text)

    context = {
        'daily_message': daily_message_obj,
        'contacts': contacts,
        'encoded_message': encoded_message,
    }
    return render(request, 'myapp/whatsapp_helper.html', context)

# ==============================================================================
# CONTACT AND GUEST MANAGEMENT VIEWS
# ==============================================================================

def invited_guests(request):
    show_arrived_only = request.GET.get("arrival") == "1"
    if show_arrived_only:
        contacts = Contact.objects.filter(invited=True, arrival_date__isnull=False, Remark__icontains="myfamily")
    else:
        contacts = Contact.objects.filter(invited=True, Remark__icontains="myfamily")
    return render(request, 'myapp/invited_guests.html', {
        'contacts': contacts,
        'filter': 'myfamily',
        'arrival_filter': show_arrived_only
    })

def edit_guest(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('invited_guests')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'myapp/edit_guest.html', {'form': form, 'contact': contact})

#def contact_list(request):
 #   contacts = Contact.objects.all()
  #  return render(request, 'myapp/contact_list.html', {'contacts': contacts})
def contact_list(request):
    """Displays all contacts."""
    contacts = Contact.objects.all()
    return render(request, 'myapp/contact_list.html', {
        'contacts': contacts,
        'filter': 'all'  # Pass a filter context
    })

def invited_contacts(request):
    """Displays only invited contacts."""
    contacts = Contact.objects.filter(invited=True)
    return render(request, 'myapp/contact_list.html', {
        'contacts': contacts,
        'filter': 'invited'
    })

def not_invited_contacts(request):
    """Displays only contacts that have not been invited."""
    contacts = Contact.objects.filter(invited=False)
    return render(request, 'myapp/contact_list.html', {
        'contacts': contacts,
        'filter': 'not_invited'
    })


def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('myapp:contact_list')
    else:
        form = ContactForm()
    return render(request, 'myapp/contact_form.html', {'form': form})

def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('myapp:contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'myapp/contact_form.html', {'form': form})

def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect('myapp:contact_list')
    return render(request, 'myapp/contact_confirm_delete.html', {'contact': contact})

# ==============================================================================
# HOTEL MANAGEMENT VIEWS
# ==============================================================================

def hotel_list(request):
    hotels = Hotel.objects.all()
    return render(request, 'myapp/hotel_list.html', {'hotels': hotels})

def hotel_create(request):
    if request.method == "POST":
        form = HotelForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('hotel_list')
    else:
        form = HotelForm()
    return render(request, 'myapp/hotel_form.html', {'form': form})

def hotel_update(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == "POST":
        form = HotelForm(request.POST, instance=hotel)
        if form.is_valid():
            form.save()
            return redirect('hotel_list')
    else:
        form = HotelForm(instance=hotel)
    return render(request, 'myapp/hotel_form.html', {'form': form})

def hotel_delete(request, pk):
    hotel = get_object_or_404(Hotel, pk=pk)
    if request.method == "POST":
        hotel.delete()
        return redirect('hotel_list')
    return render(request, 'myapp/hotel_confirm_delete.html', {'hotel': hotel})

# ==============================================================================
# DATA EXPORT AND VISUALIZATION
# ==============================================================================

def export_to_excel(request):
    try:
        data = Contact.objects.all().values()
        df = pd.DataFrame(list(data))
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="contacts.xlsx"'
        df.to_excel(response, index=False)
        return response
    except Exception as e:
        print(f"Error in export_to_excel: {e}")
        return HttpResponse("An error occurred during export. Check logs for details.")

def visitor_chart(request):
    data = Visitor.objects.annotate(date=TruncDate('visit_time')) \
                          .values('date') \
                          .annotate(count=Count('id')) \
                          .order_by('date')

    dates = [item['date'].strftime('%Y-%m-%d') for item in data]
    counts = [item['count'] for item in data]

    plt.figure(figsize=(8, 4))
    plt.plot(dates, counts, marker='o')
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('Number of Visitors')
    plt.title('Daily Site Visitors')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.close() # Important to close the plot to free up memory

    chart = base64.b64encode(image_png).decode('utf-8')
    return render(request, 'myapp/visitor_chart.html', {'chart': chart})
