from django.contrib import admin

from .models import Category


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz_list', 'created_at')
    search_fields = ('title',)
    list_filter = ('title', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('title',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    filter_horizontal = ('quizzes',)

    def quiz_list(self, obj):
        return ", ".join([q.title for q in obj.quizzes.all()])
    quiz_list.short_description = "Quiz"

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "quizzes":
            from quiz.models import Quiz
            quizzes = Quiz.objects.all()
            if quizzes.count() == 1:
                kwargs["initial"] = quizzes
        return super().formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(Category, CategoryAdmin)