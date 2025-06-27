from celery import shared_task
from django.utils import timezone

from .models import Quest


@shared_task
def update_quest_availability():
    now = timezone.now()
    quests = Quest.objects.all()
    for quest in quests:
        if quest.start_date and quest.start_date <= now:
            quest.is_active = True

        if quest.end_date and quest.end_date < now:
            quest.is_active = False

        if quest.start_date or quest.end_date:
            quest.save()
    return "Successfully updated quest availability"
