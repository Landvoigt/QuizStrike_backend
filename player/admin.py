from django.contrib import admin

from .models import Player


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('name', 'created_at')
    readonly_fields = ('created_at',)
    ordering = ('id',)
    date_hierarchy = 'created_at'
    list_per_page = 25

admin.site.register(Player, PlayerAdmin)