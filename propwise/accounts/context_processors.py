# accounts/context_processors.py

from .models import Notification

def notifications(request):
    """
    This function runs on EVERY page load.
    It makes the 'notification_count' and 'notification_list'
    available to base.html automatically.
    """
    if request.user.is_authenticated:
        # Get all unread notifications for this user
        unread_notifs = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        )
        return {
            'notification_count': unread_notifs.count(),
            'notification_list': unread_notifs[:5] # Only show the top 5 in the dropdown
        }
    
    # If user is not logged in, return nothing
    return {}