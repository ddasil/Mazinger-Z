# music_search/urls.py

from django.urls import path
from . import views
from .views import delete_mp3
from .views import save_tagged_song_view
# from .views import toggle_favorite

urlpatterns = [
    path('', views.search_view, name='music_search'),
    path('analyze-title/', views.analyze_title, name='analyze_title'),
    path('lyrics/', views.get_lyrics, name='get_lyrics'), 
    # path('translate-lyrics/', views.translate_lyrics, name='translate_lyrics'),
    path('download-mp3/', views.download_mp3, name='download_mp3'),  # ✅ 요거 추가
    path('autocomplete/', views.autocomplete, name='autocomplete'),  # 자동완성
    path('delete-mp3/', delete_mp3, name='delete_mp3'),
    path('lyrics-info/', views.lyrics_info_view, name='lyrics_info'),
    path('save-tagged-song/', save_tagged_song_view),
    # path('toggle-favorite/', toggle_favorite, name='toggle_favorite'),
]
