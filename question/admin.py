from django.contrib import admin
from django.utils.html import format_html

from answer.models import Answer

from .models import Question


def activate(modeladmin, request, queryset):
    updated_count = queryset.update(active=True)
    modeladmin.message_user(request, f"{updated_count} successfully activated questions.")

def deactivate(modeladmin, request, queryset):
    updated_count = queryset.update(active=False)
    modeladmin.message_user(request, f"{updated_count} successfully deactivated questions.")

activate.short_description = "Activate selected questions"
deactivate.short_description = "Deactivate selected questions"

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
    list_display = ('id', 'title', 'category', 'quiz', 'created_at')
    list_display_links = ('title',)
    list_filter = ('quiz', 'category', 'title')
    search_fields = ('quiz', 'category', 'title',)
    readonly_fields = ('time_ms', 'points', 'created_at', 'updated_at', 'display_image')
    ordering = ('id',)
    inlines = [AnswerInline]
    actions = [activate, deactivate, 'delete_selected']
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
            'fields': ('active', 'created_at', 'updated_at')
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
