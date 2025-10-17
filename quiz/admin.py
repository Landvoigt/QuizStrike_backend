from django.contrib import admin

from quiz.models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'updated_at')
    search_fields = ('title',)

admin.site.register(Quiz, QuizAdmin)