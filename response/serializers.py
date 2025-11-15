from rest_framework import serializers

from answer.models import Answer
from player.models import Player
from question.models import Question
from score.models import Score

from .models import Response


class ResponseSerializer(serializers.ModelSerializer):
    player_name = serializers.CharField(write_only=True, required=True)
    question_id = serializers.IntegerField(write_only=True)
    answer_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = Response
        fields = ['player_name', 'question', 'answer', 'question_id', 'answer_id', 'time']
        read_only_fields = ['question', 'answer']

    def create(self, validated_data):
        player_name = validated_data.pop("player_name")
        question_id = validated_data.pop("question_id")
        answer_id = validated_data.pop("answer_id", None)

        question = Question.objects.get(id=question_id)
        
        answer = None
        if answer_id is not None:
            answer = Answer.objects.get(id=answer_id)

        quiz = question.quiz

        player, _ = Player.objects.get_or_create(name=player_name)
        score, _ = Score.objects.get_or_create(player=player, quiz=quiz)

        validated_data["score"] = score
        validated_data["question"] = question
        validated_data["answer"] = answer

        response = super().create(validated_data)
        return response
    

class ResponseNestedSerializer(serializers.ModelSerializer):
    question_title = serializers.CharField(source='question.title', read_only=True)
    answer_text = serializers.CharField(source='answer.text', read_only=True)

    class Meta:
        model = Response
        fields = ['id', 'question_title', 'answer_text', 'time', 'created_at']
