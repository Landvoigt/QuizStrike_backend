from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from quiz.serializers import QuizSerializer
from response.models import Response as ResponseModel

from quiz.models import Quiz
from score.models import Score

from .models import Player
from .serializers import PlayerSerializer

class PlayerViewSet(ModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        quiz_id = request.data.get("quizId")

        if not name or not quiz_id:
            return Response({"error": "name and quizId are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)

        player, created = Player.objects.get_or_create(name=name)

        score, _ = Score.objects.get_or_create(player=player, quiz=quiz)

        answered_count = ResponseModel.objects.filter(score=score).count()

        total_questions = quiz.questions.count()
        quiz_completed = answered_count >= total_questions

        return Response({
            "exists": not created,
            "player_id": player.id,
            "score_id": score.id,
            "quiz_completed": quiz_completed,
            "answered_questions_count": answered_count,
            "total_questions": total_questions,
            "quiz": QuizSerializer(quiz).data
        })