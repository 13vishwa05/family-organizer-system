from django import forms
from .models import Medication, MedicationSchedule

class MedicationForm(forms.ModelForm):
    class Meta:
        model = Medication
        fields = ['family_member', 'name', 'dosage', 'instructions', 'start_date', 'end_date', 'stock_quantity', 'refill_threshold']

class MedicationScheduleForm(forms.ModelForm):
    class Meta:
        model = MedicationSchedule
        fields = ['time_of_day', 'frequency_type', 'days_of_week', 'notes']
