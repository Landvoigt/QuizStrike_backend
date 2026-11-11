from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Answer
from .serializers import AnswerSerializer

class AnswerViewSet(ReadOnlyModelViewSet):
    queryset = Answer.objects.visible()
    serializer_class = AnswerSerializer