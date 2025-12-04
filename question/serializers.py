import random

from rest_framework import serializers

from answer.models import Answer
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
        answers = list(obj.answers.all())
        random.shuffle(answers)
        return AnswerSerializer(answers, many=True).data

    def validate_answers(self, value):
        if len(value) != 4:
            raise serializers.ValidationError("Each question must have exactly 4 answers.")
        return value

    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = Question.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(question=question, **answer_data)
        return question

    def update(self, instance, validated_data):
        if 'answers' in validated_data:
            answers_data = validated_data.pop('answers')
            instance.answer_set.all().delete()
            for answer_data in answers_data:
                Answer.objects.create(question=instance, **answer_data)
        return super().update(instance, validated_data)