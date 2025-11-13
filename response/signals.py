from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Response


@receiver(post_save, sender=Response)
def update_score_after_response(sender, instance, created, **kwargs):
    if not created:
        return

    score = instance.score
    question = instance.question
    answer = instance.answer

    if not (score and question and answer):
        return

    if answer.correct:
        score.score += question.points
        score.time_only_correct += instance.time

    score.time += instance.time
    score.save()
