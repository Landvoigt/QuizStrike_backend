from django.db import models

from answer.models import Answer
from question.models import Question
from score.models import Score


class Response(models.Model):
    score = models.ForeignKey(Score, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
