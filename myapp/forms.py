from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = [
            'fname', 'lname', 'mobile', 'Address', 'Remark', 'invited',
            'arrival_date', 'mode_arrival', 'arrival_ref', 
            'room_no', 'departure_date', 'departure_ref'
        ]
        invited = forms.BooleanField(required=False)  # Checkbox for invited status
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }
###



from .models import Hotel

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'address', 'phone_number', 'tariff']
