from django.db import models


class Quiz(models.Model):
    title = models.CharField(max_length=256, unique=True)
    description = models.CharField(max_length=2048, blank=True, null=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Quiz'
        verbose_name_plural = 'Quiz'
        
    def __str__(self):
        return self.title