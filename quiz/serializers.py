from rest_framework import serializers

from .models import Quiz


class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.IntegerField(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'image', 'transparent', 'question_count', 'active', 'created_at', 'updated_at']

    def get_image(self, obj):
        return obj.image.url if obj.image else None
