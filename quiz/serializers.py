from rest_framework import serializers

from question.serializers import QuestionSerializer

from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'active', 'created_at', 'updated_at']
