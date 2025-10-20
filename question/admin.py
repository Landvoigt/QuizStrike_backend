from django.contrib import admin
from django.utils.html import format_html
from answer.models import Answer
from .models import Question


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4
    min_num = 4
    max_num = 4
    validate_min = True
    fields = ('text', 'correct')
    can_delete = False
    classes = ['wide']

    class Media:
        css = {
            'all': ('admin/css/wide-fields.css',)
        }

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('title', 'quiz', 'category', 'time', 'points', 'transparent', 'display_image')
    list_filter = ('quiz', 'category', 'transparent')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'updated_at', 'display_image')
    ordering = ('-created_at',)
    inlines = [AnswerInline]
    fields = ('quiz', 'title', 'description', 'category', 'time', 'points', 
             'image', 'display_image', 'transparent', 'created_at', 'updated_at')

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No image"
    display_image.short_description = 'Image Preview'

admin.site.register(Question, QuestionAdmin)
