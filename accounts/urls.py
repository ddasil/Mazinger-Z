from django.urls import path, include
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mypage/', include('mypage.urls')),  # mypage 앱의 URL을 추가
    path('check_nickname/', views.check_nickname, name='check_nickname'),
    path('find_username/', views.find_username, name='find_username'),
    path('find_password/', views.find_password, name='find_password'),
    path('reset_password/<str:uid>/', views.reset_password, name='reset_password'),
    path('check_username/', views.check_username, name='check_username'),  # AJAX 용
]
