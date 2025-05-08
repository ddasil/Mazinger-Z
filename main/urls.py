from django.urls import path, include
from . import views
from .views import preference_view # 메인 음악 취향 검사

urlpatterns = [
    path('', views.main, name='main'),
    path('accounts/', include('accounts.urls')),  # accounts 앱의 URL을 포함시킴
    path('lyricsgen/', include('lyricsgen.urls')),  # lyricsgen 앱의 URL을 포함시킴
    path('mypage/', include('mypage.urls')),  # mypage 앱의 URL을 포함시킴
    path('analyze/', include('analyze.urls')),  # analyze 앱 연결
    path('music/', include('music_search.urls')), # music_search 앱 연결
    path('recommend/', include('recommendations.urls')), # recommendations 앱연결
    path('preference/', preference_view, name='preference'), # 메인 음악 취향 검사
    path("recommend_by_genre/", views.recommend_by_genre, name="recommend_by_genre"), # 메인 음악 취향 검사 추천 음악
]
