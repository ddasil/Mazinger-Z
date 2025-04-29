from django.urls import path
from . import views

urlpatterns = [
    path('', views.mypage, name='mypage'),  # 마이페이지 뷰 연결
]

