# lyricsgen/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lyrics_home, name='lyrics_root'),  # ✅ 이거 추가
    path('generate/', views.generate_lyrics, name='generate_lyrics'),
    path('lyrics/', views.lyrics_home, name='lyrics'),
    path('edit/<int:pk>/', views.edit_lyrics, name='edit_lyrics'),
    path('delete/<int:pk>/', views.delete_lyrics, name='delete_lyrics'),
    path('logout/', views.logout_view, name='logout'),
]
