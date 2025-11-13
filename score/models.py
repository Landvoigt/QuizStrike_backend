from django.db import models

from quiz.models import Quiz
from player.models import Player


class Score(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="scores", on_delete=models.CASCADE)
    player = models.ForeignKey(Player, related_name="scores", on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    time = models.IntegerField(default=0)
    time_only_correct = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('player', 'quiz')

    def __str__(self):
        return f"{self.player.name} - {self.quiz.title} ({self.score} pts)"