from django.db import models
from families.models import FamilyMember

APPOINTMENT_STATUS_CHOICES = (
    ('UPCOMING', 'Upcoming'),
    ('COMPLETED', 'Completed'),
    ('CANCELLED', 'Cancelled'),
)

class Appointment(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='appointments')
    doctor_name = models.CharField(max_length=255)
    hospital_or_clinic_name = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default='UPCOMING')

    def __str__(self):
        return f"{self.family_member} with {self.doctor_name} on {self.date_time}"
