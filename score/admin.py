from django.contrib import admin

from response.models import Response

from .models import Score


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    fields = ('question', 'answer', 'time')

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('score', 'player', 'time', 'created_at')
    list_display_links = ('player',)
    search_fields = ('player__name', 'quiz__title')
    list_filter = ('score', 'player', 'time', 'created_at')
    readonly_fields = ('token', 'created_at')
    ordering = ('-score',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [ResponseInline]

admin.site.register(Score, ScoreAdmin)