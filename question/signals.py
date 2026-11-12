from django.db.models.signals import m2m_changed, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from quiz.models import Quiz

from .models import Question


@receiver(post_save, sender=Question)
@receiver(pre_delete, sender=Question)
def update_quiz_timestamp(sender, instance, **kwargs):
    Quiz.objects.filter(questions=instance).update(updated_at=timezone.now())


@receiver(m2m_changed, sender=Question.quiz.through)
def update_assigned_quiz_timestamp(sender, instance, action, reverse, pk_set, **kwargs):
    if action not in ("post_add", "post_remove", "pre_clear"):
        return
    if reverse:
        quizzes = Quiz.objects.filter(pk=instance.pk)
    elif action == "pre_clear":
        quizzes = Quiz.objects.filter(questions=instance)
    else:
        quizzes = Quiz.objects.filter(pk__in=pk_set)
    quizzes.update(updated_at=timezone.now())
