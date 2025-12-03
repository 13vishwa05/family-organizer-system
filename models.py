from django.db import models
from django.contrib.auth.models import User

NOTIFICATION_TYPE_CHOICES = (
    ('MEDICATION_DUE', 'Medication Due'),
    ('APPOINTMENT_REMINDER', 'Appointment Reminder'),
    ('REFILL_DUE', 'Refill Due'),
)

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} - {self.type} - {self.message[:30]}"
