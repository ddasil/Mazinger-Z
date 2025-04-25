# lyricsgen/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # path('', views.lyrics_home, name='lyrics_home'),
    path('generate/', views.generate_lyrics, name='generate_lyrics'),
    path('', views.lyrics_home, name='home'),

]