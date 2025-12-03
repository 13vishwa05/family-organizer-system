from django.db import models
from django.contrib.auth.models import User

class FamilyGroup(models.Model):
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_families')
    invite_code = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, through='FamilyMembership', related_name='family_groups')

    def __str__(self):
        return self.name

class FamilyMembership(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Admin'),
        ('MEMBER', 'Member'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    family_group = models.ForeignKey(FamilyGroup, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='MEMBER')

    class Meta:
        unique_together = ('user', 'family_group')

class FamilyMember(models.Model):
    family_group = models.ForeignKey(FamilyGroup, on_delete=models.CASCADE, related_name='family_members')
    name = models.CharField(max_length=255)
    relationship = models.CharField(max_length=100)
    date_of_birth = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.relationship})"
