from rest_framework import serializers

from response.serializers import ResponseNestedSerializer

from .models import Score


class ScoreSerializer(serializers.ModelSerializer):
    responses = ResponseNestedSerializer(many=True, read_only=True)
    
    class Meta:
        model = Score
        fields = ['id','quiz', 'player', 'score', 'time', 'responses', 'created_at', 'updated_at']