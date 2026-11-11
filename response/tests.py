import threading
from datetime import timedelta

from django.conf import settings
from django.db import connection
from django.test import TestCase, TransactionTestCase, skipUnlessDBFeature
from django.utils import timezone
from rest_framework.test import APIClient

from answer.models import Answer
from category.models import Category
from player.models import Player
from question.models import Question
from quiz.models import Quiz
from score.models import Score

from .models import Response


def create_quiz(question_count=1, points=3, title="Quiz"):
    quiz = Quiz.objects.create(title=title)
    category = Category.objects.create(title=f"{title} category")
    correct_answers = []
    for i in range(question_count):
        question = Question.objects.create(quiz=quiz, category=category, title=f"{title} question {i}", points=points)
        correct_answers.append(Answer.objects.create(question=question, text="right", correct=True))
        for text in ("wrong 1", "wrong 2", "wrong 3"):
            Answer.objects.create(question=question, text=text)
    return quiz, correct_answers


def join(client, quiz, player_name="player", token=None):
    headers = {"X-Player-Token": token} if token else {}
    return client.post("/api/player/", {"name": player_name, "quizId": quiz.id}, format="json", headers=headers)


def token_for(quiz, player_name):
    """Behaves like the frontend: join once, then reuse the stored token."""
    score = Score.objects.filter(quiz=quiz, player__name=player_name).first()
    if score is None:
        return join(APIClient(), quiz, player_name).data["token"]
    return score.token


def start(client, quiz, player_name="player", token=None):
    token = token or token_for(quiz, player_name)
    return client.post(
        "/api/start/", {"player_name": player_name, "quiz_id": quiz.id}, format="json",
        headers={"X-Player-Token": token},
    )


def finish(client, response_id, answer_id, time=None, token=None):
    if token is None:
        response = Response.objects.select_related("score").filter(id=response_id).first()
        token = response.score.token if response else "unknown"
    data = {"response_id": response_id, "answer_id": answer_id}
    if time is not None:
        data["time"] = time
    return client.post("/api/finish/", data, format="json", headers={"X-Player-Token": token})


def started_ago(response_id, milliseconds):
    Response.objects.filter(id=response_id).update(created_at=timezone.now() - timedelta(milliseconds=milliseconds))


class QuizFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def assertAbout(self, value, expected, tolerance=500):
        self.assertGreaterEqual(value, expected)
        self.assertLess(value, expected + tolerance)

    def test_start_does_not_reveal_the_solution(self):
        quiz, _ = create_quiz()

        answers = start(self.client, quiz).data["question"]["answers"]

        self.assertEqual(len(answers), 4)
        self.assertTrue(all("correct" not in answer for answer in answers))

    def test_list_endpoints_do_not_reveal_the_solution(self):
        create_quiz()

        answers = list(self.client.get("/api/answer/").data)
        answers += self.client.get("/api/question/").data[0]["answers"]
        answers += self.client.get("/api/category/").data[0]["questions"][0]["answers"]

        self.assertEqual(len(answers), 12)
        self.assertTrue(all("correct" not in answer for answer in answers))

    def test_correct_answer_adds_points_and_server_measured_time(self):
        quiz, (correct,) = create_quiz(points=3)

        started = start(self.client, quiz)
        self.assertEqual(started.status_code, 201)
        self.assertEqual(started.data["remaining_questions"], 1)
        self.assertEqual(started.data["answered_questions"], 0)
        self.assertEqual(started.data["total_questions"], 1)

        started_ago(started.data["response_id"], 1500)
        finished = finish(self.client, started.data["response_id"], correct.id)

        self.assertEqual(finished.status_code, 200)
        self.assertTrue(finished.data["correct"])
        self.assertEqual(finished.data["correct_answer_id"], correct.id)
        self.assertEqual(finished.data["points"], 3)
        self.assertFalse(finished.data["timed_out"])
        self.assertAbout(finished.data["time"], 1500)

        score = Score.objects.get()
        self.assertEqual(score.score, 3)
        self.assertAbout(score.time, 1500)
        self.assertEqual(score.time_only_correct, score.time)
        self.assertTrue(start(self.client, quiz).data["quiz_completed"])

    def test_plausible_client_time_is_used(self):
        quiz, (correct,) = create_quiz()
        response_id = start(self.client, quiz).data["response_id"]
        started_ago(response_id, 3000)

        finished = finish(self.client, response_id, correct.id, time=2400)

        self.assertEqual(finished.data["time"], 2400)
        self.assertEqual(Score.objects.get().time, 2400)

    def test_too_fast_client_time_is_raised_to_server_time_minus_grace(self):
        quiz, (correct,) = create_quiz()
        response_id = start(self.client, quiz).data["response_id"]
        started_ago(response_id, 5000)

        finished = finish(self.client, response_id, correct.id, time=1)

        self.assertAbout(finished.data["time"], 5000 - settings.QUIZ_ANSWER_GRACE_MS)

    def test_client_time_above_server_time_is_capped(self):
        quiz, (correct,) = create_quiz()
        response_id = start(self.client, quiz).data["response_id"]
        started_ago(response_id, 3000)

        finished = finish(self.client, response_id, correct.id, time=9000)

        self.assertAbout(finished.data["time"], 3000)

    def test_negative_client_time_is_rejected(self):
        quiz, (correct,) = create_quiz()
        response_id = start(self.client, quiz).data["response_id"]

        self.assertEqual(finish(self.client, response_id, correct.id, time=-5).status_code, 400)

    def test_wrong_or_missing_answer_adds_only_time(self):
        quiz, (first_correct, second_correct) = create_quiz(question_count=2)
        wrong = Answer.objects.filter(correct=False, question=start(self.client, quiz).data["question"]["id"]).first()
        response = Response.objects.get()
        started_ago(response.id, 500)

        finished = finish(self.client, response.id, wrong.id)
        self.assertFalse(finished.data["correct"])
        self.assertIn(finished.data["correct_answer_id"], {first_correct.id, second_correct.id})
        self.assertEqual(finished.data["points"], 0)

        second = start(self.client, quiz)
        started_ago(second.data["response_id"], 700)
        finish(self.client, second.data["response_id"], None)

        score = Score.objects.get()
        self.assertEqual((score.score, score.time_only_correct), (0, 0))
        self.assertAbout(score.time, 1200)

    def test_answer_within_grace_period_counts(self):
        quiz, (correct,) = create_quiz(points=3)
        response_id = start(self.client, quiz).data["response_id"]
        started_ago(response_id, 11000)

        finished = finish(self.client, response_id, correct.id)

        self.assertTrue(finished.data["correct"])
        self.assertEqual(finished.data["time"], 10000)
        self.assertEqual(Score.objects.get().score, 3)

    def test_answer_after_time_limit_and_grace_period_scores_nothing(self):
        quiz, (correct,) = create_quiz(points=3)
        response_id = start(self.client, quiz).data["response_id"]
        started_ago(response_id, 10000 + settings.QUIZ_ANSWER_GRACE_MS + 1000)

        finished = finish(self.client, response_id, correct.id)

        self.assertEqual(finished.status_code, 200)
        self.assertTrue(finished.data["timed_out"])
        self.assertFalse(finished.data["correct"])
        self.assertEqual(finished.data["correct_answer_id"], correct.id)
        self.assertEqual(finished.data["time"], 10000)
        score = Score.objects.get()
        self.assertEqual((score.score, score.time, score.time_only_correct), (0, 10000, 0))
        self.assertIsNone(Response.objects.get().answer)

    def test_answer_of_another_question_is_rejected(self):
        quiz, correct_answers = create_quiz(question_count=2)
        started = start(self.client, quiz)
        other_correct = next(a for a in correct_answers if a.question_id != started.data["question"]["id"])

        finished = finish(self.client, started.data["response_id"], other_correct.id)

        self.assertEqual(finished.status_code, 400)
        self.assertIsNone(Response.objects.get().finished_at)
        self.assertEqual(Score.objects.get().score, 0)

    def test_finishing_twice_is_rejected_and_counted_once(self):
        quiz, (correct,) = create_quiz(points=3)
        response_id = start(self.client, quiz).data["response_id"]

        self.assertEqual(finish(self.client, response_id, correct.id).status_code, 200)
        self.assertEqual(finish(self.client, response_id, correct.id).status_code, 409)

        self.assertEqual(Score.objects.get().score, 3)

    def test_unknown_response_or_answer_is_rejected(self):
        quiz, _ = create_quiz()
        response_id = start(self.client, quiz).data["response_id"]

        self.assertEqual(finish(self.client, 999999, None).status_code, 400)
        self.assertEqual(finish(self.client, response_id, 999999).status_code, 400)
        self.assertIsNone(Response.objects.get(id=response_id).finished_at)

    def test_start_never_repeats_a_question(self):
        quiz, _ = create_quiz(question_count=5)
        seen = {start(self.client, quiz).data["question"]["id"] for _ in range(5)}

        self.assertEqual(len(seen), 5)
        self.assertTrue(start(self.client, quiz).data["quiz_completed"])


class InactiveObjectsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.quiz, self.correct_answers = create_quiz(question_count=3)
        self.inactive_question = Question.objects.get(title="Quiz question 0")
        self.inactive_question.active = False
        self.inactive_question.save()

    def get_ids(self, url):
        return {item["id"] for item in self.client.get(url).data}

    def test_start_never_serves_inactive_questions(self):
        served = []
        for _ in range(2):
            started = start(self.client, self.quiz)
            self.assertEqual(started.data["total_questions"], 2)
            served.append(started.data["question"]["id"])

        self.assertNotIn(self.inactive_question.id, served)
        self.assertTrue(start(self.client, self.quiz).data["quiz_completed"])

    def test_inactive_category_hides_all_its_questions(self):
        Category.objects.update(active=False)

        self.assertTrue(start(self.client, self.quiz).data["quiz_completed"])
        self.assertEqual(self.get_ids("/api/question/"), set())
        self.assertEqual(self.get_ids("/api/category/"), set())

    def test_inactive_quiz_cannot_be_listed_or_started(self):
        token = join(self.client, self.quiz).data["token"]
        Quiz.objects.update(active=False)

        self.assertEqual(self.get_ids("/api/quiz/"), set())
        self.assertEqual(start(self.client, self.quiz, token=token).status_code, 404)
        self.assertEqual(
            self.client.post("/api/player/", {"name": "p", "quizId": self.quiz.id}, format="json").status_code, 404
        )

    def test_list_endpoints_hide_inactive_objects(self):
        self.assertNotIn(self.inactive_question.id, self.get_ids("/api/question/"))
        category_question_ids = {q["id"] for q in self.client.get("/api/category/").data[0]["questions"]}
        self.assertNotIn(self.inactive_question.id, category_question_ids)
        self.assertEqual(len(category_question_ids), 2)
        self.assertFalse(
            Answer.objects.filter(question=self.inactive_question, id__in=self.get_ids("/api/answer/")).exists()
        )

    def test_inactive_answers_are_not_shown(self):
        hidden = Answer.objects.filter(correct=False).exclude(question=self.inactive_question).first()
        hidden.active = False
        hidden.save()

        shown = set()
        for _ in range(2):
            shown |= {a["id"] for a in start(self.client, self.quiz).data["question"]["answers"]}
        self.assertNotIn(hidden.id, shown)
        self.assertNotIn(hidden.id, self.get_ids("/api/answer/"))

    def test_inactive_players_are_hidden_from_players_and_scores(self):
        start(self.client, self.quiz, player_name="hidden")
        start(self.client, self.quiz, player_name="visible")
        Player.objects.filter(name="hidden").update(active=False)

        self.assertEqual({p["name"] for p in self.client.get("/api/player/").data}, {"visible"})
        self.assertEqual({s["player"]["name"] for s in self.client.get("/api/score/").data}, {"visible"})


class WriteAccessTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.quiz, (self.correct,) = create_quiz()
        self.question = self.correct.question
        start(self.client, self.quiz)
        self.score = Score.objects.get()
        self.player = self.score.player

    def test_content_and_score_endpoints_are_read_only(self):
        objects = {
            "quiz": self.quiz,
            "category": self.question.category,
            "question": self.question,
            "answer": self.correct,
            "score": self.score,
            "player": self.player,
        }
        for name, obj in objects.items():
            with self.subTest(endpoint=name):
                self.assertEqual(self.client.get(f"/api/{name}/{obj.id}/").status_code, 200)
                self.assertEqual(self.client.put(f"/api/{name}/{obj.id}/", {}, format="json").status_code, 405)
                self.assertEqual(self.client.patch(f"/api/{name}/{obj.id}/", {}, format="json").status_code, 405)
                self.assertEqual(self.client.delete(f"/api/{name}/{obj.id}/").status_code, 405)
                if name != "player":
                    self.assertEqual(self.client.post(f"/api/{name}/", {}, format="json").status_code, 405)

        self.assertEqual(Question.objects.count(), 1)
        self.assertEqual(Score.objects.count(), 1)

    def test_player_can_still_join_a_quiz(self):
        joined = self.client.post("/api/player/", {"name": "new", "quizId": self.quiz.id}, format="json")

        self.assertEqual(joined.status_code, 200)
        self.assertFalse(joined.data["exists"])
        self.assertEqual(joined.data["total_questions"], 1)

    def test_response_endpoint_is_gone(self):
        self.assertEqual(self.client.get("/api/response/").status_code, 404)


class PlayerTokenTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.quiz, (self.correct,) = create_quiz()

    def test_join_returns_a_token_and_rejoin_needs_it(self):
        joined = join(self.client, self.quiz, "lisa")
        self.assertEqual(joined.status_code, 200)
        token = joined.data["token"]
        self.assertGreaterEqual(len(token), 40)

        self.assertEqual(join(self.client, self.quiz, "lisa").status_code, 409)
        self.assertEqual(join(self.client, self.quiz, "lisa", token="wrong").status_code, 409)

        rejoined = join(self.client, self.quiz, "lisa", token=token)
        self.assertEqual(rejoined.status_code, 200)
        self.assertTrue(rejoined.data["exists"])
        self.assertEqual(rejoined.data["token"], token)

    def test_same_name_gets_a_new_token_for_another_quiz(self):
        other_quiz, _ = create_quiz(title="Other")
        first = join(self.client, self.quiz, "lisa").data["token"]

        second = join(APIClient(), other_quiz, "lisa")

        self.assertEqual(second.status_code, 200)
        self.assertNotEqual(second.data["token"], first)
        self.assertEqual(Player.objects.filter(name="lisa").count(), 1)

    def test_start_requires_the_token_of_this_player_and_quiz(self):
        other_quiz, _ = create_quiz(title="Other")
        lisa = join(self.client, self.quiz, "lisa").data["token"]
        lisa_other_quiz = join(self.client, other_quiz, "lisa").data["token"]
        max_token = join(self.client, self.quiz, "max").data["token"]

        self.assertEqual(start(self.client, self.quiz, "lisa", token="wrong").status_code, 403)
        self.assertEqual(start(self.client, self.quiz, "lisa", token=max_token).status_code, 403)
        self.assertEqual(start(self.client, self.quiz, "lisa", token=lisa_other_quiz).status_code, 403)
        self.assertEqual(start(self.client, self.quiz, "nobody", token=lisa).status_code, 403)
        no_header = self.client.post("/api/start/", {"player_name": "lisa", "quiz_id": self.quiz.id}, format="json")
        self.assertEqual(no_header.status_code, 403)
        self.assertFalse(Response.objects.exists())

        self.assertEqual(start(self.client, self.quiz, "lisa", token=lisa).status_code, 201)

    def test_finish_rejects_another_players_token(self):
        response_id = start(self.client, self.quiz, "lisa").data["response_id"]
        max_token = join(self.client, self.quiz, "max").data["token"]

        self.assertEqual(finish(self.client, response_id, self.correct.id, token=max_token).status_code, 403)
        self.assertEqual(finish(self.client, response_id, self.correct.id, token="").status_code, 403)
        self.assertIsNone(Response.objects.get().finished_at)
        self.assertEqual(Score.objects.get(player__name="lisa").score, 0)

        self.assertEqual(finish(self.client, response_id, self.correct.id).status_code, 200)

    def test_token_is_not_exposed_by_list_endpoints(self):
        token = join(self.client, self.quiz, "lisa").data["token"]

        for url in ("/api/score/", "/api/player/"):
            self.assertNotIn(token, self.client.get(url).content.decode())


@skipUnlessDBFeature("has_select_for_update")
class ConcurrencyTests(TransactionTestCase):
    """Real concurrent requests in separate threads and DB connections (Postgres only)."""

    def run_parallel(self, func, count=8):
        barrier = threading.Barrier(count)
        results = []

        def worker():
            try:
                barrier.wait()
                results.append(func())
            finally:
                connection.close()

        threads = [threading.Thread(target=worker) for _ in range(count)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return results

    def test_parallel_finish_counts_points_once(self):
        quiz, (correct,) = create_quiz(points=3)
        response_id = start(APIClient(), quiz).data["response_id"]

        codes = self.run_parallel(lambda: finish(APIClient(), response_id, correct.id).status_code)

        self.assertEqual(sorted(codes), [200] + [409] * 7)
        self.assertEqual(Score.objects.get().score, 3)

    def test_parallel_start_hands_out_distinct_questions(self):
        quiz, _ = create_quiz(question_count=8)
        start(APIClient(), quiz)  # create player and score up front
        Response.objects.all().delete()

        results = self.run_parallel(lambda: start(APIClient(), quiz).data)

        question_ids = [r["question"]["id"] for r in results]
        self.assertEqual(len(set(question_ids)), 8)
