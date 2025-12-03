from django.urls import path
from . import views

urlpatterns = [
    path('refill/', views.refill_reminders_view, name='refill_reminders'),
]
