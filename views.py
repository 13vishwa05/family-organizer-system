from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from families.models import FamilyMember
from .models import Medication, MedicationSchedule, MedicationIntakeLog
from .forms import MedicationForm, MedicationScheduleForm
from .utils import get_user_primary_family, get_scheduled_doses_for_day, calculate_compliance

@login_required
def medications_list(request, member_id=None):
    fg = get_user_primary_family(request.user)
    members = fg.family_members.all() if fg else []
    selected_member = None
    meds = Medication.objects.none()
    if member_id:
        selected_member = get_object_or_404(FamilyMember, id=member_id, family_group=fg)
        meds = selected_member.medications.all().prefetch_related('schedules')
    return render(request, 'medications/medications_list.html', {
        'family_group': fg,
        'members': members,
        'selected_member': selected_member,
        'medications': meds,
    })

@login_required
def medication_create(request):
    fg = get_user_primary_family(request.user)
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        form.fields['family_member'].queryset = fg.family_members.all()
        if form.is_valid():
            med = form.save()
            return redirect('medications:medications_list', med.family_member.id)
    else:
        form = MedicationForm()
        form.fields['family_member'].queryset = fg.family_members.all()
    return render(request, 'medications/medication_form.html', {'form': form})

@login_required
def medication_edit(request, med_id):
    med = get_object_or_404(Medication, id=med_id)
    fg = get_user_primary_family(request.user)
    if med.family_member.family_group != fg:
        return redirect('medications:medications_list')
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=med)
        form.fields['family_member'].queryset = fg.family_members.all()
        if form.is_valid():
            form.save()
            return redirect('medications:medications_list', med.family_member.id)
    else:
        form = MedicationForm(instance=med)
        form.fields['family_member'].queryset = fg.family_members.all()
    return render(request, 'medications/medication_form.html', {'form': form, 'medication': med})

@login_required
def schedule_add(request, med_id):
    med = get_object_or_404(Medication, id=med_id)
    fg = get_user_primary_family(request.user)
    if med.family_member.family_group != fg:
        return redirect('medications:medications_list')
    if request.method == 'POST':
        form = MedicationScheduleForm(request.POST)
        if form.is_valid():
            sch = form.save(commit=False)
            sch.medication = med
            sch.save()
            return redirect('medications:medications_list', med.family_member.id)
    else:
        form = MedicationScheduleForm()
    return render(request, 'medications/medication_form.html', {'form': form, 'medication': med, 'schedule_only': True})

@login_required
def daily_checklist(request):
    fg = get_user_primary_family(request.user)
    members = fg.family_members.all() if fg else []
    date_str = request.GET.get('date')
    member_id = request.GET.get('member')
    if date_str:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        target_date = timezone.localdate()
    selected_member = None
    if member_id:
        selected_member = get_object_or_404(FamilyMember, id=member_id, family_group=fg)
    doses = get_scheduled_doses_for_day(fg, target_date, selected_member)

    if request.method == 'POST':
        schedule_id = request.POST.get('schedule_id')
        action = request.POST.get('action')  # TAKEN / MISSED
        sch = get_object_or_404(MedicationSchedule, id=schedule_id)
        fm = sch.medication.family_member
        log, created = MedicationIntakeLog.objects.get_or_create(
            medication_schedule=sch,
            family_member=fm,
            date=target_date,
            defaults={'marked_by': request.user, 'status': action}
        )
        if not created:
            log.status = action
            log.marked_by = request.user
            log.time = timezone.now().time()
            log.save()
        return redirect(f"{request.path}?date={target_date.isoformat()}&member={member_id or ''}")

    return render(request, 'medications/daily_checklist.html', {
        'family_group': fg,
        'members': members,
        'selected_member': selected_member,
        'target_date': target_date,
        'doses': doses,
    })

@login_required
def stats_view(request):
    fg = get_user_primary_family(request.user)
    members = fg.family_members.all() if fg else []
    selected_member = None
    stats = None
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    member_id = request.GET.get('member')

    from datetime import date, timedelta
    today = timezone.localdate()
    default_start = today - timedelta(days=30)

    if member_id:
        selected_member = get_object_or_404(FamilyMember, id=member_id, family_group=fg)
    if selected_member:
        if start_date_str:
            start = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        else:
            start = default_start
        if end_date_str:
            end = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            end = today
        stats = calculate_compliance(selected_member, start, end)

    return render(request, 'medications/stats.html', {
        'family_group': fg,
        'members': members,
        'selected_member': selected_member,
        'stats': stats,
    })
