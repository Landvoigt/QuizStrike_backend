from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone

from quiz.models import Quiz

from .models import Answer


@receiver([post_save, post_delete], sender=Answer)
def update_quiz_timestamp(sender, instance, **kwargs):
    Quiz.objects.filter(questions=instance.question_id).update(updated_at=timezone.now())
