from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from medications.utils import get_today_dashboard_context

def dashboard_view(request):
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('accounts:login')
    context = get_today_dashboard_context(request.user)
    return render(request, 'dashboard.html', context)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include(('accounts.urls', 'accounts'), namespace='accounts')),
    path('families/', include(('families.urls', 'families'), namespace='families')),
    path('medications/', include(('medications.urls', 'medications'), namespace='medications')),
    path('appointments/', include(('appointments.urls', 'appointments'), namespace='appointments')),
    path('notifications/', include(('notifications.urls', 'notifications'), namespace='notifications')),
    path('', dashboard_view, name='dashboard'),
]
