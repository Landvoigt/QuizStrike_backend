from django.contrib import admin
from django.utils.html import format_html

from .models import Quiz


class QuizAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description', 'question_count', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'question_list', 'category_list')
    ordering = ('id',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Configuration', {
            'fields': ('title', 'description')
        }),
        ('Questions', {
            'fields': ('question_list',)
        }),
        ('Categories', {
            'fields': ('category_list',)
        }),
        ('Creation Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def question_list(self, obj):
        questions = obj.questions.all()
        return format_html(
            "<br>".join([
                "<a href='/admin/question/question/{}/change/' style='line-height: 1.75;'>• {}</a>".format(q.id, q.title)
                for q in questions
            ])
        )
    
    def category_list(self, obj):
        categories = obj.categories.all()
        return format_html(
            "<br>".join([
                "<a href='/admin/category/category/{}/change/' style='line-height: 1.75;'>• {}</a>".format(c.id, c.title)
                for c in categories
            ])
        )

    def question_count(self, obj):
        return obj.questions.count()

    question_list.short_description = "Questions"
    question_count.short_description = "Question Count"
    category_list.short_description = "Categories"

admin.site.register(Quiz, QuizAdmin)