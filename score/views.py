from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Score
from .serializers import ScoreSerializer


class ScoreViewSet(ReadOnlyModelViewSet):
    queryset = Score.objects.filter(player__active=True).select_related("player")
    serializer_class = ScoreSerializer
