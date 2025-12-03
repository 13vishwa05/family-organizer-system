from django.test import TestCase
from django.contrib.auth.models import User
from datetime import date, time
from families.models import FamilyGroup, FamilyMembership, FamilyMember
from .models import Medication, MedicationSchedule, MedicationIntakeLog
from .utils import calculate_compliance

class ComplianceTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test', password='test')
        self.family = FamilyGroup.objects.create(name='Test Family', created_by=self.user)
        FamilyMembership.objects.create(user=self.user, family_group=self.family, role='ADMIN')
        self.member = FamilyMember.objects.create(
            family_group=self.family,
            name='Grandma',
            relationship='Grandmother'
        )
        self.med = Medication.objects.create(
            family_member=self.member,
            name='TestMed',
            dosage='1 tab',
            start_date=date.today()
        )
        self.schedule = MedicationSchedule.objects.create(
            medication=self.med,
            time_of_day=time(8, 0),
            frequency_type='DAILY'
        )

    def test_compliance_all_taken(self):
        today = date.today()
        MedicationIntakeLog.objects.create(
            medication_schedule=self.schedule,
            family_member=self.member,
            date=today,
            status='TAKEN',
            marked_by=self.user
        )
        stats = calculate_compliance(self.member, today, today)
        self.assertEqual(stats['total_doses'], 1)
        self.assertEqual(stats['taken_doses'], 1)
        self.assertEqual(stats['compliance_percent'], 100.0)
