from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Answer


@receiver([post_save, post_delete], sender=Answer)
def update_quiz_timestamp(sender, instance, **kwargs):
    if instance.question.quiz_id:
        instance.question.quiz.save()
