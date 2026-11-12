from rest_framework import serializers

from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = '__all__'


class PlayerJoinSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=Player._meta.get_field("name").max_length)
    quizId = serializers.IntegerField()
