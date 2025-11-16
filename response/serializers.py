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


class ResponseFinishSerializer(serializers.ModelSerializer):
    answer_id = serializers.IntegerField(required=False)
    player_name = serializers.CharField()
    question_id = serializers.IntegerField()

    class Meta:
        model = Response
        fields = ("player_name", "question_id", "time", "answer_id")

    def validate(self, attrs):
        try:
            player = Player.objects.get(name=attrs["player_name"])
        except Player.DoesNotExist:
            raise serializers.ValidationError("Player not found")

        try:
            question = Question.objects.get(id=attrs["question_id"])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question not found")

        try:
            score = player.scores.get(quiz=question.quiz)
        except:
            raise serializers.ValidationError("Score not found")

        try:
            response = Response.objects.get(score=score, question=question)
        except Response.DoesNotExist:
            raise serializers.ValidationError("Response not found")

        attrs["instance"] = response
        return attrs

    def update(self, instance, validated_data):
        instance.time = validated_data["time"]

        answer_id = validated_data.get("answer_id")
        if answer_id is not None:
            instance.answer = Answer.objects.get(id=answer_id)

        instance.save()
        return instance
