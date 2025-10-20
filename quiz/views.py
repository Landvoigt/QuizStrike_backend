from rest_framework.viewsets import ModelViewSet

from .models import Quiz
from .serializers import QuizSerializer

class QuizViewSet(ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer