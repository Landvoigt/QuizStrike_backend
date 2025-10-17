from django.db import models

from player.models import Player


class Score(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    time = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
