from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=2048)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title