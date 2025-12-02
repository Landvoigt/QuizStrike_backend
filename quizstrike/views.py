from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
import random

from player.models import Player
from question.serializers import QuestionSerializer
from quiz.models import Quiz
from response.models import Response
from score.models import Score

from .serializers import QuestionStartSerializer, QuestionFinishSerializer
from django.db import transaction
from rest_framework.response import Response as DRFResponse


class QuestionStartView(APIView):
    serializer_class = QuestionStartSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        player_name = serializer.validated_data["player_name"]
        quiz_id = serializer.validated_data["quiz_id"]

        quiz = get_object_or_404(Quiz, id=quiz_id)

        player, _ = Player.objects.get_or_create(name=player_name)
        score, _ = Score.objects.get_or_create(player=player, quiz=quiz)

        answered_ids = set(
            Response.objects.filter(score=score)
            .values_list("question_id", flat=True)
        )

        all_questions = quiz.questions.all()

        remaining = all_questions.exclude(id__in=answered_ids)

        if not remaining.exists():
            return DRFResponse({
                "quiz_completed": True,
                "message": "All questions answered",
                "remaining_questions": 0,
            })

        question = random.choice(list(remaining))

        response_obj = Response.objects.create(
            score=score,
            question=question,
            answer=None,
            time=question.time
        )

        return DRFResponse({
            "quiz_completed": False,
            "response_id": response_obj.id,
            "question": QuestionSerializer(question).data,
            "remaining_questions": remaining.count(),
            "answered_questions": len(answered_ids),
            "total_questions": all_questions.count()
        }, status=status.HTTP_201_CREATED)


class QuestionFinishView(APIView):
    serializer_class = QuestionFinishSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.validated_data["instance"]
        serializer.update(instance, serializer.validated_data)

        return DRFResponse({"status": "ok"}, status=status.HTTP_200_OK)
