from django.db import models

from answer.models import Answer
from question.models import Question
from score.models import Score


class Response(models.Model):
    score = models.ForeignKey(Score, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="responses", on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="responses", on_delete=models.CASCADE, null=True, blank=True)
    time = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.score.player.name} → {self.question.title}"
