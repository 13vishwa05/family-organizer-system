from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from families.models import FamilyMember
from .models import Appointment
from .forms import AppointmentForm
from medications.utils import get_user_primary_family

@login_required
def appointments_list(request):
    fg = get_user_primary_family(request.user)
    members = fg.family_members.all() if fg else []
    member_id = request.GET.get('member')
    qs = Appointment.objects.filter(family_member__family_group=fg).order_by('date_time')
    selected_member = None
    if member_id:
        selected_member = get_object_or_404(FamilyMember, id=member_id, family_group=fg)
        qs = qs.filter(family_member=selected_member)
    return render(request, 'appointments/appointments_list.html', {
        'appointments': qs,
        'members': members,
        'selected_member': selected_member,
    })

@login_required
def appointment_create(request):
    fg = get_user_primary_family(request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        form.fields['family_member'].queryset = fg.family_members.all()
        if form.is_valid():
            form.save()
            return redirect('appointments:appointments_list')
    else:
        form = AppointmentForm()
        form.fields['family_member'].queryset = fg.family_members.all()
    return render(request, 'appointments/appointment_form.html', {'form': form})

@login_required
def appointment_edit(request, appt_id):
    fg = get_user_primary_family(request.user)
    appt = get_object_or_404(Appointment, id=appt_id, family_member__family_group=fg)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appt)
        form.fields['family_member'].queryset = fg.family_members.all()
        if form.is_valid():
            form.save()
            return redirect('appointments:appointments_list')
    else:
        form = AppointmentForm(instance=appt)
        form.fields['family_member'].queryset = fg.family_members.all()
    return render(request, 'appointments/appointment_form.html', {'form': form})
