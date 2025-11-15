from rest_framework import serializers

from answer.models import Answer
from player.models import Player
from question.models import Question
from score.models import Score

from .models import Response


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Response
        fields = ['player_name', 'question', 'answer', 'question_id', 'answer_id', 'time']
        read_only_fields = ['question', 'answer']


class ResponseNestedSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='question.title', read_only=True)
    answer_text = serializers.CharField(source='answer.text', read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'question_title', 'answer_text', 'time', 'created_at']


class ResponseStartSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(write_only=True)
    question_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Response
        fields = ["player_name", "question_id"]

    def create(self, validated_data):
        player_name = validated_data.pop("player_name")
        question_id = validated_data["question_id"]

        question = Question.objects.get(id=question_id)
        player, _ = Player.objects.get_or_create(name=player_name)
        score, _ = Score.objects.get_or_create(player=player, quiz=question.quiz)

        response_instance, _ = Response.objects.get_or_create(
            score=score,
            question=question,
            answer=None,
            time=question.time
        )
        return response_instance


class ResponseFinishSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    question_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    time = serializers.IntegerField()
