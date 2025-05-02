from django.contrib import admin
from .models import ChartSong

@admin.register(ChartSong)
class ChartSongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'normalized_genre')
    search_fields = ('title', 'artist', 'normalized_genre')
