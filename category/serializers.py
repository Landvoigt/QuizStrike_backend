from rest_framework import serializers

from question.serializers import QuestionSerializer

from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'

    def get_questions(self, obj):
        questions = [question for question in obj.questions.all() if question.active]
        return QuestionSerializer(questions, many=True).data
