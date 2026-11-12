from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Quiz
from .serializers import QuizSerializer

class QuizViewSet(ReadOnlyModelViewSet):
    queryset = Quiz.objects.filter(active=True).with_question_count().order_by("id")
    serializer_class = QuizSerializer
