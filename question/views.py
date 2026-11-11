from rest_framework.viewsets import ReadOnlyModelViewSet

from .models import Question
from .serializers import QuestionSerializer


class QuestionViewSet(ReadOnlyModelViewSet):
    queryset = (
        Question.objects.visible()
        .select_related("category")
        .prefetch_related("answers")
    )
    serializer_class = QuestionSerializer