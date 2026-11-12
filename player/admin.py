from django.contrib import admin

from score.models import Score

from .models import Player


class ScoreInline(admin.TabularInline):
    model = Score
    extra = 0
    fields = ('quiz', 'score', 'time', 'token', 'created_at')
    readonly_fields = fields
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('id',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    inlines = [ScoreInline]

admin.site.register(Player, PlayerAdmin)
