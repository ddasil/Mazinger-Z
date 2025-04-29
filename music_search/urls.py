# music_search/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.search_view, name='music_search'),
    path('analyze-title/', views.analyze_title, name='analyze_title'),
    path('lyrics/', views.get_lyrics, name='get_lyrics'), 
    path('translate-lyrics/', views.translate_lyrics, name='translate_lyrics'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),  # 자동완성
]
