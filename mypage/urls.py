from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.mypage, name='mypage'),  # 마이페이지 뷰 연결
    path('music/', include('music_search.urls')), # music_search 앱 연결
    path('verify-password/', views.verify_password, name='verify_password'),
]
