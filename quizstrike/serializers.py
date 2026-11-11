from rest_framework import serializers

from response.models import Response


class QuestionStartSerializer(serializers.Serializer):
    player_name = serializers.CharField()
    quiz_id = serializers.IntegerField()


class QuestionFinishSerializer(serializers.Serializer):
    response_id = serializers.IntegerField()
    answer_id = serializers.IntegerField(required=False, allow_null=True)
    time = serializers.IntegerField(required=False, allow_null=True, min_value=0)

    def validate(self, attrs):
        if not Response.objects.filter(id=attrs["response_id"]).exists():
            raise serializers.ValidationError("Response not found")
        return attrs
