from django.db import models


class QuizQuerySet(models.QuerySet):
    def with_question_count(self):
        visible = models.Q(questions__active=True, questions__category__active=True)
        return self.annotate(question_count=models.Count("questions", filter=visible, distinct=True))


class Quiz(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuizQuerySet.as_manager()

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
        
    def __str__(self):
        return self.title
