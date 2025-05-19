import matplotlib
matplotlib.use('Agg')
from django.shortcuts import render, redirect, get_object_or_404, redirect
from .models import Contact
from .forms import ContactForm
from .models import Hotel
from .forms import HotelForm

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

#def invited_guests(request):
 #   contacts = Contact.objects.filter(invited=True, Remark__icontains="myfamily")
#    return render(request, 'myapp/invited_guests.html', {'contacts': contacts, 'filter': 'myfamily'})

def edit_guest(request, contact_id):
    contact = get_object_or_404(Contact, id=contact_id)
    
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('invited_guests')  # Redirect back to guest list
    
    else:
        form = ContactForm(instance=contact)
    
    return render(request, 'myapp/edit_guest.html', {'form': form, 'contact': contact})

def invited_contacts(request):
    contacts = Contact.objects.filter(invited=True)  # Show only invited contacts
    return render(request, 'myapp/contact_list.html', {'contacts': contacts, 'filter': 'invited'})

def not_invited_contacts(request):
    contacts = Contact.objects.filter(invited=False)  # Show only NOT invited contacts
    return render(request, 'myapp/contact_list.html', {'contacts': contacts, 'filter': 'not_invited'})

def all_contacts(request):
    contacts = Contact.objects.all()  # Fetch all contacts
    return render(request, 'myapp/contact_list.html', {'contacts': contacts, 'filter': 'all'})

def contact_list(request):
    contacts = Contact.objects.all()
    return render(request, 'myapp/contact_list.html', {'contacts': contacts})

def contact_create(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm()
    return render(request, 'myapp/contact_form.html', {'form': form})

def contact_edit(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            return redirect('contact_list')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'myapp/contact_form.html', {'form': form})

def contact_delete(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    if request.method == "POST":
        contact.delete()
        return redirect('contact_list')
    return render(request, 'myapp/contact_confirm_delete.html', {'contact': contact})
###


import pandas as pd
from django.http import HttpResponse

def export_to_excel(request):
    try:
        # Retrieve data from the database
        data = Contact.objects.all().values()  # Fetch Contact data
        print("Data retrieved:", data)  # Debugging: Print the data to the console
        
        # Convert the data to a Pandas DataFrame
        df = pd.DataFrame(list(data))
        print("DataFrame created:", df)  # Debugging: Ensure DataFrame is created

        # Create a response with Excel content
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="data.xlsx"'

        # Write the DataFrame to an Excel file
        df.to_excel(response, index=False)
        print("Export to Excel view was called")
        return response
    except Exception as e:
        print(f"Error occurred: {e}")  # Log the error in the console for debugging
        return HttpResponse("An error occurred. Check the logs for more details.")



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


import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.utils.timezone import now
from .models import Visitor
from django.db.models.functions import TruncDate
from django.db.models import Count

def visitor_chart(request):
    # Group visitors by date
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
    plt.ylabel('Visitors')
    plt.title('Daily Visitors')
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    chart = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'myapp/visitor_chart.html', {'chart': chart})
