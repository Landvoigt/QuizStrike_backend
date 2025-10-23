from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Category


@receiver([post_save, post_delete], sender=Category)
def update_quiz_timestamp(sender, instance, **kwargs):
    if instance.quiz_id:
        instance.quiz.save()
