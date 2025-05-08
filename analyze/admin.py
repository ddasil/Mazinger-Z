from django.contrib import admin
from .models import UserSong, Song

@admin.register(UserSong)
class UserSongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'top3_emotions', 'user', 'created_at')

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'top2_emotions', 'created_at')