from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.urls import reverse
from django.utils.html import format_html_join
from django.utils.safestring import mark_safe

from question.models import Question

from .models import Quiz


class QuizAdminForm(forms.ModelForm):
    # Reverse side of Question.quiz, so questions can be picked while editing a quiz.
    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.select_related('category').order_by('category__title', 'title'),
        required=False,
        widget=FilteredSelectMultiple('Questions', is_stacked=False),
    )

    class Meta:
        model = Quiz
        fields = ('title', 'description', 'active')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['questions'].initial = self.instance.questions.all()


class QuizAdmin(admin.ModelAdmin):
    form = QuizAdminForm
    list_display = ('id', 'title', 'description', 'question_count', 'active', 'created_at')
    list_display_links = ('title',)
    search_fields = ('title', 'description')
    list_filter = ('active', 'created_at', 'updated_at')
    readonly_fields = ('created_at', 'updated_at', 'category_list')
    ordering = ('id',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    fieldsets = (
        ('Configuration', {
            'fields': ('title', 'description', 'active')
        }),
        ('Questions', {
            'fields': ('questions',)
        }),
        ('Categories', {
            'fields': ('category_list',)
        }),
        ('Creation Information', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.questions.set(form.cleaned_data['questions'])

    def category_list(self, obj):
        return format_html_join(
            mark_safe("<br>"),
            "<a href='{}' style='line-height: 1.75;'>• {}</a>",
            (
                (reverse("admin:category_category_change", args=[c.id]), c.title)
                for c in obj.categories.all()
            ),
        )

    def question_count(self, obj):
        return obj.questions.count()

    question_count.short_description = "Question Count"
    category_list.short_description = "Categories"

admin.site.register(Quiz, QuizAdmin)
