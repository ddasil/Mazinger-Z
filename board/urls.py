# board/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.post_list, name='post_list'),              # 게시판 메인
    path('new/', views.post_create, name='post_create'),      # 글쓰기 페이지
    path('<int:pk>/', views.post_detail, name='post_detail'),  # ✅ 상세페이지 URL
    path('<int:pk>/like/', views.like_post, name='like_post'),
]

