from django.urls import path
from . import views
from .views import toggle_lovelist

urlpatterns = [
    path('', views.post_list, name='post_list'),                 # 게시판 메인
    path('new/', views.post_create, name='post_create'),         # 글쓰기 페이지
    path('<int:pk>/', views.post_detail, name='post_detail'),    # 상세 페이지
    path('<int:pk>/like/', views.like_post, name='like_post'),   # 좋아요
    path('comment/<int:comment_id>/reply/', views.comment_reply, name='comment_reply'),  # ✅ 대댓글
    path("scrap/<int:pk>/", views.scrap_post, name="scrap_post"),
    path('edit/<int:pk>/', views.post_edit, name='post_edit'),
    path('delete/<int:pk>/', views.post_delete, name='post_delete'),
    path('lovelist/toggle/', toggle_lovelist, name='toggle_lovelist'),
]
