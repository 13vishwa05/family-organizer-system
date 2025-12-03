from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from medications.models import RefillReminder
from medications.utils import get_user_primary_family

@login_required
def refill_reminders_view(request):
    fg = get_user_primary_family(request.user)
    reminders = RefillReminder.objects.filter(
        medication__family_member__family_group=fg,
        is_resolved=False
    )
    return render(request, 'notifications/refill_reminders.html', {'reminders': reminders})
