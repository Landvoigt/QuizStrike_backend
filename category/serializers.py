from rest_framework import serializers

from question.serializers import QuestionSerializer

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    class Meta:
        model = Category
        fields = '__all__'
