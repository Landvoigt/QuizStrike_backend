from django.contrib import admin

from response.models import Response

from .models import Score


class ResponseInline(admin.TabularInline):
    model = Response
    extra = 0
    fields = ('question', 'answer', 'time')

    # def has_add_permission(self, request):
    #     return False

class ScoreAdmin(admin.ModelAdmin):
    list_display = ('score', 'player', 'time', 'created_at')
    search_fields = ('score', 'player', 'time',)
    list_filter = ('score', 'player', 'time', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('score',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [ResponseInline]

    # def has_add_permission(self, request):
    #     return False

admin.site.register(Score, ScoreAdmin)