from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response as DRFResponse
from rest_framework.views import APIView

from answer.models import Answer
from question.serializers import QuestionSerializer
from quiz.models import Quiz
from response.models import Response
from score.models import Score

from .serializers import QuestionStartSerializer, QuestionFinishSerializer


class QuestionStartView(APIView):
    serializer_class = QuestionStartSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        player_name = serializer.validated_data["player_name"]
        quiz_id = serializer.validated_data["quiz_id"]

        quiz = get_object_or_404(Quiz, id=quiz_id, active=True)

        score = Score.objects.filter(player__name=player_name, quiz=quiz).first()
        if score is None or not score.has_token(request.headers.get("X-Player-Token")):
            return DRFResponse({"error": "Invalid player token"}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            # Lock this player's score row: concurrent start requests of the same
            # player run one after another and never receive the same question.
            Score.objects.select_for_update().filter(pk=score.pk).first()

            answered_ids = Response.objects.filter(score=score).values("question_id")
            all_questions = quiz.questions.visible()
            remaining = all_questions.exclude(id__in=answered_ids)

            total_count = all_questions.count()
            remaining_count = remaining.count()

            if remaining_count == 0:
                return DRFResponse({
                    "quiz_completed": True,
                    "message": "All questions answered",
                    "remaining_questions": 0,
                })

            question = (
                remaining.select_related("category")
                .prefetch_related("answers")
                .order_by("?")
                .first()
            )

            response_obj = Response.objects.create(
                score=score,
                question=question,
                answer=None,
                time=question.time,
            )

        return DRFResponse({
            "quiz_completed": False,
            "response_id": response_obj.id,
            "question": QuestionSerializer(question).data,
            "remaining_questions": remaining_count,
            "answered_questions": total_count - remaining_count,
            "total_questions": total_count,
        }, status=status.HTTP_201_CREATED)


class QuestionFinishView(APIView):
    serializer_class = QuestionFinishSerializer

    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        # Lock the response row: a second, concurrent finish request waits here
        # until the first one has committed and then sees finished_at already set.
        response = (
            Response.objects.select_for_update(of=("self",))
            .select_related("question", "score")
            .get(id=data["response_id"])
        )

        if not response.score.has_token(request.headers.get("X-Player-Token")):
            return DRFResponse({"error": "Invalid player token"}, status=status.HTTP_403_FORBIDDEN)

        if response.finished_at is not None:
            return DRFResponse(
                {"error": "Response already finished"},
                status=status.HTTP_409_CONFLICT,
            )

        question = response.question

        answer = None
        answer_id = data.get("answer_id")
        if answer_id is not None:
            answer = Answer.objects.filter(id=answer_id, question=question, active=True).first()
            if answer is None:
                return DRFResponse(
                    {"error": "Answer not found for this question"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # The server-measured time includes network latency and image loading, so the
        # client's timer is trusted as long as it lies within the grace period below it.
        grace = settings.QUIZ_ANSWER_GRACE_MS
        now = timezone.now()
        elapsed = int((now - response.created_at).total_seconds() * 1000)
        client_time = data.get("time")
        if client_time is None:
            client_time = elapsed
        measured = min(max(client_time, elapsed - grace), elapsed)

        timed_out = elapsed > question.time + grace
        if timed_out:
            answer = None

        response.answer = answer
        response.time = max(0, min(measured, question.time))
        response.finished_at = now
        response.save(update_fields=["answer", "time", "finished_at"])

        correct = answer is not None and answer.correct
        points = question.points if correct else 0

        # Increment atomically in the database (UPDATE ... SET score = score + x),
        # so no points are lost when requests run concurrently.
        Score.objects.filter(pk=response.score_id).update(
            score=F("score") + points,
            time=F("time") + response.time,
            time_only_correct=F("time_only_correct") + (response.time if correct else 0),
            updated_at=now,
        )

        correct_answer_id = (
            question.answers.filter(correct=True, active=True).values_list("id", flat=True).first()
        )

        return DRFResponse({
            "status": "ok",
            "correct": correct,
            "correct_answer_id": correct_answer_id,
            "points": points,
            "time": response.time,
            "timed_out": timed_out,
        }, status=status.HTTP_200_OK)
