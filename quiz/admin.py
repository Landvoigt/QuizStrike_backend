from django.contrib import admin
from django.utils.html import format_html, format_html_join

from category.models import Category

from .models import Quiz


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 0
    fields = ('title',)
    classes = ['wide']

    class Media:
        css = {
            'all': ('quizstrike/css/admin_custom.css',)
        }

class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'description', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'question_list')
    ordering = ('title',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [CategoryInline]
    fieldsets = (
        ('Configuration', {
            'fields': ('title', 'description')
        }),
        ('Questions', {
            'fields': ('question_list',)
        }),
        ('Creation Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def question_list(self, obj):
        questions = obj.questions.all()
        
        return format_html(
            "<ul>{}</ul>",
            format_html_join(
                "", "<li>{}: {}</li>",
                ((p.id, p.title) for p in questions)
            )
        )
    
    def question_count(self, obj):
        return obj.questions.count()

    question_list.short_description = "Questions"
    question_count.short_description = "Question Count"

admin.site.register(Quiz, QuizAdmin)