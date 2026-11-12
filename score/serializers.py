from rest_framework import serializers

from player.models import Player

from .models import Score


class ScorePlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = ['name']


class ScoreSerializer(serializers.ModelSerializer):
    player = ScorePlayerSerializer(read_only=True)

    class Meta:
        model = Score
        fields = ['id', 'score', 'time', 'player']
