# mypage/urls.py
from django.urls import path, include
from . import views  # 여기서 views.mypage 등 다 처리

urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('verify_password/', views.verify_password, name='verify_password'),  # ✅ 고쳤음
    path('user-generated-lyrics/', views.user_generated_lyrics, name='user_generated_lyrics'),  # ✅ 이 줄!
    path('music/', include('music_search.urls')),
]
