from django.db import models

from question.models import Question


class AnswerQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(active=True, question__active=True, question__category__active=True)


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name="answers", on_delete=models.CASCADE)
    text = models.CharField(max_length=2048)
    correct = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AnswerQuerySet.as_manager()

    def __str__(self):
        return self.text