from django.db import models
from django.contrib.auth.models import User
from families.models import FamilyMember
from django.utils import timezone

class Medication(models.Model):
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='medications')
    name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    stock_quantity = models.IntegerField(blank=True, null=True)
    refill_threshold = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} for {self.family_member}"

    def is_active_on(self, date):
        if self.start_date and date < self.start_date:
            return False
        if self.end_date and date > self.end_date:
            return False
        return True

FREQUENCY_CHOICES = (
    ('DAILY', 'Daily'),
    ('WEEKDAYS', 'Weekdays'),
    ('CUSTOM_DAYS', 'Custom Days'),
)

DAYS_OF_WEEK_CHOICES = (
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
)

class MedicationSchedule(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='schedules')
    time_of_day = models.TimeField()
    frequency_type = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='DAILY')
    # Store comma-separated days like "MON,TUE"
    days_of_week = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.medication.name} at {self.time_of_day}"

    def applies_on_date(self, date):
        import datetime
        weekday = date.weekday()  # Monday=0
        code = ['MON','TUE','WED','THU','FRI','SAT','SUN'][weekday]

        if self.frequency_type == 'DAILY':
            return True
        elif self.frequency_type == 'WEEKDAYS':
            return code in ['MON','TUE','WED','THU','FRI']
        elif self.frequency_type == 'CUSTOM_DAYS':
            if not self.days_of_week:
                return False
            days = self.days_of_week.split(',')
            return code in days
        return False

INTAKE_STATUS_CHOICES = (
    ('TAKEN', 'Taken'),
    ('MISSED', 'Missed'),
    ('SKIPPED', 'Skipped'),
)

class MedicationIntakeLog(models.Model):
    medication_schedule = models.ForeignKey(MedicationSchedule, on_delete=models.CASCADE, related_name='intake_logs')
    family_member = models.ForeignKey(FamilyMember, on_delete=models.CASCADE, related_name='intake_logs')
    date = models.DateField()
    time = models.TimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=INTAKE_STATUS_CHOICES)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('medication_schedule', 'family_member', 'date')

    def __str__(self):
        return f"{self.family_member} {self.date} {self.status}"

class RefillReminder(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='refill_reminders')
    estimated_run_out_date = models.DateField()
    reminder_date = models.DateField()
    is_resolved = models.BooleanField(default=False)
    resolution_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Refill {self.medication} by {self.reminder_date}"
