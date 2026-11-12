from rest_framework import serializers

from player.serializers import PlayerSerializer

from .models import Score


class ScoreSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)

    class Meta:
        model = Score
        fields = ['id', 'quiz', 'player', 'score', 'time', 'created_at', 'updated_at']
