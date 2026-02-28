from .models import Country, GuideMessage

def countries_context(request):
    return {
        'countries': Country.objects.all()
    }


def unread_messages_context(request):
    """Add unread message count to context"""
    if request.user.is_authenticated:
        if hasattr(request.user, 'guide'):
            # For guides: count unread messages from travelers
            unread_count = GuideMessage.objects.filter(
                booking__guide=request.user.guide,
                is_read=False
            ).exclude(sender=request.user).count()
        else:
            # For travelers: count unread messages from guides
            unread_count = GuideMessage.objects.filter(
                booking__user=request.user,
                is_read=False
            ).exclude(sender=request.user).count()
        
        return {'unread_message_count': unread_count}
    
    return {'unread_message_count': 0}
