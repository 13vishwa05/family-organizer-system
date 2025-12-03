from django import forms
from .models import FamilyMember, FamilyGroup

class FamilyGroupForm(forms.ModelForm):
    class Meta:
        model = FamilyGroup
        fields = ['name']

class FamilyMemberForm(forms.ModelForm):
    class Meta:
        model = FamilyMember
        fields = ['name', 'relationship', 'date_of_birth', 'notes']
