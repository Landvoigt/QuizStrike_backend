from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Response


@receiver(post_save, sender=Response)
def update_score_after_response(sender, instance, created, **kwargs):
    if created:
        return

    score = instance.score
    question = instance.question

    if not (score and question):
        return
    
    if instance.answer and instance.answer.correct:
        score.score += question.points
        score.time_only_correct += instance.time

    score.time += instance.time
    score.save()
