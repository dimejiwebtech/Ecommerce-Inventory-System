from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import staff_required
from .models import ActivityLog
from accounts.models import CustomUser

@staff_required
def ims_activity_history(request):
    logs = ActivityLog.objects.all().select_related('user')
    
    # Simple Filters
    action = request.GET.get('action')
    user_id = request.GET.get('user')
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    if action:
        logs = logs.filter(action_type=action)
    if user_id:
        logs = logs.filter(user_id=user_id)
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
        
    staff_users = CustomUser.objects.filter(is_staff=True)
    
    context = {
        'logs': logs[:500],
        'staff_users': staff_users,
        'action_choices': ActivityLog.ACTION_CHOICES,
        'filters': {
            'action': action,
            'user_id': user_id,
            'date_from': date_from,
            'date_to': date_to,
        }
    }
    return render(request, 'ims/activity_history.html', context)
