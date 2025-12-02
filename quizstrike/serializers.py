from rest_framework import serializers

from answer.models import Answer
from response.models import Response


class QuestionStartSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    quiz_id = serializers.IntegerField()


class QuestionFinishSerializer(serializers.Serializer):
    response_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    time = serializers.IntegerField()

    def validate(self, attrs):
        try:
            response = Response.objects.get(id=attrs["response_id"])
        except Response.DoesNotExist:
            raise serializers.ValidationError("Response not found")

        attrs["instance"] = response
        return attrs

    def update(self, instance, validated_data):
        instance.time = validated_data["time"]

        answer_id = validated_data.get("answer_id")
        if answer_id is not None:
            instance.answer = Answer.objects.get(id=answer_id)

        instance.save()
        return instance
