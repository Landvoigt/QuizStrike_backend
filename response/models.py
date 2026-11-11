from django.db import models

from answer.models import Answer
from question.models import Question
from score.models import Score


class Response(models.Model):
    score = models.ForeignKey(Score, related_name="responses", on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name="responses", on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, related_name="responses", on_delete=models.CASCADE, null=True, blank=True)
    time = models.IntegerField(default=0)
    finished_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["score", "question"], name="unique_response_per_score_question"),
        ]

    def __str__(self):
        return f"{self.score.player.name} → {self.question.title}"
