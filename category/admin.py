from django.contrib import admin
from django.utils.html import format_html

from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'quiz_list', 'question_count', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title',)
    list_filter = ('title', 'created_at')
    readonly_fields = ('created_at', 'image_preview')
    date_hierarchy = 'created_at'
    list_per_page = 25
    filter_horizontal = ('quizzes',)
    fields = ('quizzes', 'title', 'image', 'image_preview', 'transparent', 'active', 'created_at')

    def quiz_list(self, obj):
        return ", ".join([q.title for q in obj.quizzes.all()])
    quiz_list.short_description = "Quiz"

    def question_count(self, obj):
        return obj.questions.count()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "quizzes":
            from quiz.models import Quiz
            quizzes = Quiz.objects.all()
            if quizzes.count() == 1:
                kwargs["initial"] = quizzes
        return super().formfield_for_manytomany(db_field, request, **kwargs)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No image"
    image_preview.short_description = 'Image Preview'
    
    question_count.short_description = "Question Count"

admin.site.register(Category, CategoryAdmin)