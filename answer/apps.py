from django.apps import AppConfig


class AnswerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'answer'

    def ready(self):
        __import__('answer.signals')
