from django.contrib import admin

from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)
    list_filter = ('name', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('name',)
    date_hierarchy = 'created_at'
    list_per_page = 25

admin.site.register(Player, PlayerAdmin)