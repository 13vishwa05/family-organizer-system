from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_family_group, name='create_family_group'),
    path('<int:family_id>/members/', views.family_members_list, name='family_members_list'),
    path('<int:family_id>/members/add/', views.family_member_create, name='family_member_create'),
    path('<int:family_id>/members/<int:member_id>/edit/', views.family_member_edit, name='family_member_edit'),
    path('<int:family_id>/members/<int:member_id>/delete/', views.family_member_delete, name='family_member_delete'),
]
