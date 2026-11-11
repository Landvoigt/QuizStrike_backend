from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Quiz
from .serializers import QuizSerializer

class QuizViewSet(ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(active=True)
    serializer_class = QuizSerializer