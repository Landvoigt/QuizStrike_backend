from rest_framework import serializers

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
