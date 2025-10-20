from rest_framework.viewsets import ModelViewSet

from .models import Answer
from .serializers import AnswerSerializer

class AnswerViewSet(ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer