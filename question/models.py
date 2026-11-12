from django.db import models

from quiz.models import Quiz
from category.models import Category


class QuestionQuerySet(models.QuerySet):
    def visible(self):
        return self.filter(active=True, category__active=True)


class Question(models.Model):
    quiz = models.ManyToManyField(Quiz, related_name='questions')
    title = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='questions', on_delete=models.CASCADE)
    time = models.IntegerField(default=10000)
    points = models.IntegerField(default=1)
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    transparent = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = QuestionQuerySet.as_manager()

    def __str__(self):
        return self.title