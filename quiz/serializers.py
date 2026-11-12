from rest_framework import serializers

from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'question_count', 'active', 'created_at', 'updated_at']
