from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.response import Response
from rest_framework import status
from quiz.serializers import QuizSerializer
from response.models import Response as ResponseModel

from quiz.models import Quiz
from score.models import Score

from .models import Player
from .serializers import PlayerSerializer

class PlayerViewSet(ReadOnlyModelViewSet):
    queryset = Player.objects.filter(active=True)
    serializer_class = PlayerSerializer

    def create(self, request, *args, **kwargs):
        name = request.data.get("name")
        quiz_id = request.data.get("quizId")

        if not name or not quiz_id:
            return Response({"error": "name and quizId are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            quiz = Quiz.objects.get(id=quiz_id, active=True)
        except Quiz.DoesNotExist:
            return Response({"error": "Quiz not found"}, status=404)

        player, created = Player.objects.get_or_create(name=name)

        # Each player+quiz combination gets its own token: the same name can play
        # another quiz from another browser, but nobody else can take over a running one.
        score, score_created = Score.objects.get_or_create(player=player, quiz=quiz)
        if not score_created and not score.has_token(request.headers.get("X-Player-Token")):
            return Response({"error": "Name already taken"}, status=status.HTTP_409_CONFLICT)

        visible_questions = quiz.questions.visible()
        answered_count = ResponseModel.objects.filter(score=score, question__in=visible_questions).count()

        total_questions = visible_questions.count()
        quiz_completed = answered_count >= total_questions

        return Response({
            "exists": not created,
            "player_id": player.id,
            "score_id": score.id,
            "token": score.token,
            "quiz_completed": quiz_completed,
            "answered_questions": answered_count,
            "total_questions": total_questions,
            "quiz": QuizSerializer(quiz).data
        })