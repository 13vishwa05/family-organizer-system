from django.urls import path
from . import views

urlpatterns = [
    path('', views.appointments_list, name='appointments_list'),
    path('add/', views.appointment_create, name='appointment_create'),
    path('<int:appt_id>/edit/', views.appointment_edit, name='appointment_edit'),
]
