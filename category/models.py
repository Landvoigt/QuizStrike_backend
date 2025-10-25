from django.db import models

from quiz.models import Quiz


class Category(models.Model):
    quizzes = models.ManyToManyField("quiz.Quiz", related_name="categories")
    title = models.CharField(max_length=256, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from quiz.models import Quiz
        if self.quizzes.count() == 0:
            quizzes = Quiz.objects.all()
            if quizzes.count() == 1:
                self.quizzes.add(quizzes.first())