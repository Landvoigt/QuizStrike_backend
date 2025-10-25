from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Category


@receiver([post_save, post_delete], sender=Category)
def update_quiz_timestamp(sender, instance, **kwargs):
    for quiz in instance.quizzes.all():
        quiz.save()
