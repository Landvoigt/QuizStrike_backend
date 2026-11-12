from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Score
from .serializers import ScoreSerializer


class ScoreListQuerySerializer(serializers.Serializer):
    quiz = serializers.IntegerField()


class ScoreViewSet(ReadOnlyModelViewSet):
    queryset = Score.objects.filter(player__active=True, quiz__active=True).select_related("player")
    serializer_class = ScoreSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "list":
            params = ScoreListQuerySerializer(data=self.request.query_params)
            params.is_valid(raise_exception=True)
            queryset = queryset.filter(quiz_id=params.validated_data["quiz"]).order_by("-score", "time", "id")
        return queryset
