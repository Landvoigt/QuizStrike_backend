from rest_framework import serializers

from player.models import Player
from score.models import Score

from .models import Response


class ResponseSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Response
        fields = ['player_name', 'question', 'answer', 'time']

    def create(self, validated_data):
        player_name = validated_data.pop("player_name")
        question = validated_data["question"]
        answer = validated_data["answer"]
        quiz = question.quiz

        player, _ = Player.objects.get_or_create(name=player_name)
        score, _ = Score.objects.get_or_create(player=player, quiz=quiz)

        validated_data["score"] = score
        response = super().create(validated_data)
        return response
    

class ResponseNestedSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='question.title', read_only=True)
    answer_text = serializers.CharField(source='answer.text', read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'question_title', 'answer_text', 'time', 'created_at']
