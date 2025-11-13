from rest_framework import serializers

from answer.models import Answer
from answer.serializers import AnswerSerializer

from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)
    category_title = serializers.SerializerMethodField()
    class Meta:
        model = Question
        fields = '__all__'

    def get_category_title(self, obj):
        return obj.category.title if obj.category else None

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