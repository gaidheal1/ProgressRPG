from celery import shared_task
from django.utils import timezone
from .models import Quest

@shared_task
def update_quest_availability():
    now = timezone.now()
    quests = Quest.objects.all()
    for quest in quests:
        if quest.end_date < now:
            quest.is_active = False
            quest.save()
        elif quest.start_date <= now <quest.end_date:
            quest.is_active = True
        quest.save()
    return 'Successfully updated quest availability'
