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
            'all': ('quizstrike/css/admin_custom.css',)
        }

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'category', 'title', 'transparent', 'display_image', 'created_at')
    list_filter = ('quiz', 'category', 'title')
    search_fields = ('quiz', 'category', 'title',)
    readonly_fields = ('time_ms', 'points', 'created_at', 'updated_at', 'display_image')
    ordering = ('title',)
    inlines = [AnswerInline]
    fieldsets = (
        ('Selection', {
            'fields': ('quiz', 'category')
        }),
        ('Configuration', {
            'fields': ('title', 'description', 'image', 'display_image', 'transparent')
        }),
        ('Standards', {
            'fields': ('time_ms', 'points')
        }),
        ('Creation Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def time_ms(self, obj):
        if obj and obj.time is not None:
            return f"{obj.time} ms"
        return "-"
    time_ms.short_description = 'time'
    time_ms.admin_order_field = 'time'

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" />', obj.image.url)
        return "No image"
    display_image.short_description = 'Image Preview'

admin.site.register(Question, QuestionAdmin)
