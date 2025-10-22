from rest_framework import serializers

from question.serializers import QuestionSerializer

from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Quiz
        fields = '__all__'