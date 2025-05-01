from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/', include('accounts.urls')),  # accounts 앱의 URL을 포함시킴
    path('lyricsgen/', include('lyricsgen.urls')),  # lyricsgen 앱의 URL을 포함시킴
    path('mypage/', include('mypage.urls')),  # mypage 앱의 URL을 포함시킴
    path('analyze/', include('analyze.urls')),  # analyze 앱 연결
    path('music/', include('music_search.urls')) # music_search 앱 연결
]
