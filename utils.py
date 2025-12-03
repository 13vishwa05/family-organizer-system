from datetime import date, timedelta
from django.utils import timezone
from families.models import FamilyGroup, FamilyMember
from .models import MedicationSchedule, MedicationIntakeLog, RefillReminder
from appointments.models import Appointment

def get_user_primary_family(user):
    return user.family_groups.first()

def get_scheduled_doses_for_day(family_group, target_date, member=None):
    """Return list of dicts representing scheduled doses for given day."""
    schedules = MedicationSchedule.objects.filter(
        medication__family_member__family_group=family_group
    ).select_related('medication', 'medication__family_member')

    if member:
        schedules = schedules.filter(medication__family_member=member)

    doses = []
    for sch in schedules:
        med = sch.medication
        if not med.is_active_on(target_date):
            continue
        if not sch.applies_on_date(target_date):
            continue
        fm = med.family_member
        log = MedicationIntakeLog.objects.filter(
            medication_schedule=sch,
            family_member=fm,
            date=target_date
        ).first()
        doses.append({
            'schedule': sch,
            'medication': med,
            'family_member': fm,
            'time_of_day': sch.time_of_day,
            'status': log.status if log else None,
            'log': log,
        })
    # sort by time
    doses.sort(key=lambda d: d['time_of_day'])
    return doses

def calculate_compliance(family_member, start_date, end_date):
    fg = family_member.family_group
    total = 0
    taken = 0
    current = start_date
    while current <= end_date:
        doses = get_scheduled_doses_for_day(fg, current, member=family_member)
        for d in doses:
            total += 1
            if d['status'] == 'TAKEN':
                taken += 1
        current += timedelta(days=1)
    percent = (taken / total * 100) if total > 0 else 0
    return {
        'total_doses': total,
        'taken_doses': taken,
        'compliance_percent': round(percent, 1),
    }

def update_refill_reminders_for_medication(medication):
    """Simple logic: assumes all schedules daily, count schedules as doses/day."""
    if medication.stock_quantity is None or medication.refill_threshold is None:
        return
    schedules = medication.schedules.all()
    doses_per_day = len(schedules)
    if doses_per_day == 0:
        return
    # approximate from today onwards
    today = date.today()
    days_left = medication.stock_quantity / doses_per_day
    est_run_out = today + timedelta(days=int(days_left))
    # remind 3 days before
    reminder_date = est_run_out - timedelta(days=3)
    rr, created = RefillReminder.objects.get_or_create(
        medication=medication,
        estimated_run_out_date=est_run_out,
        reminder_date=reminder_date,
        is_resolved=False,
    )
    return rr

def get_today_dashboard_context(user):
    today = timezone.localdate()
    fg = get_user_primary_family(user)
    members = fg.family_members.all() if fg else []
    doses = get_scheduled_doses_for_day(fg, today) if fg else []
    upcoming_appointments = Appointment.objects.filter(
        family_member__family_group=fg,
        status='UPCOMING',
        date_time__date=today
    ).order_by('date_time') if fg else []
    refill_alerts = RefillReminder.objects.filter(
        medication__family_member__family_group=fg,
        is_resolved=False,
        reminder_date__lte=today
    ) if fg else []
    return {
        'family_group': fg,
        'members': members,
        'today_doses': doses,
        'appointments_today': upcoming_appointments,
        'refill_alerts': refill_alerts,
        'today': today,
    }
