import random

from rest_framework import serializers

from answer.serializers import AnswerSerializer
from category.models import Category

from .models import Question


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('title', 'image', 'transparent', 'active', 'created_at', 'updated_at')
        

class QuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    category = CategorySimpleSerializer(read_only=True)
    class Meta:
        model = Question
        fields = '__all__'

    def get_answers(self, obj):
        answers = [answer for answer in obj.answers.all() if answer.active]
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data