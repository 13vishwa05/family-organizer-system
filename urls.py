from django.urls import path
from . import views

urlpatterns = [
    path('', views.medications_list, name='medications_list'),
    path('member/<int:member_id>/', views.medications_list, name='medications_list'),
    path('add/', views.medication_create, name='medication_create'),
    path('<int:med_id>/edit/', views.medication_edit, name='medication_edit'),
    path('<int:med_id>/schedule/add/', views.schedule_add, name='schedule_add'),
    path('checklist/', views.daily_checklist, name='daily_checklist'),
    path('stats/', views.stats_view, name='stats'),
]
