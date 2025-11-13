# In portfolio/forms.py

from django import forms
from .models import Holding

class HoldingForm(forms.ModelForm):
    class Meta:
        model = Holding
        # Exclude the user field, as it will be set automatically in the view
        exclude = ('user',)
        # Add Bootstrap widget attributes if needed, e.g., for date picker
        widgets = {
            'purchase_date': forms.DateInput(attrs={'type': 'date'}),
        }
