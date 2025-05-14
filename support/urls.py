from django.urls import path
from . import views

urlpatterns = [
    path('', views.support_board_list, name='support_board_list'),
    path('create/', views.support_board_create, name='support_board_create'),
    path('<int:pk>/', views.support_board_detail, name='support_board_detail'),
    path('<int:pk>/reply/', views.support_board_reply, name='support_board_reply'),
    path('<int:pk>/delete/', views.support_board_delete, name='support_board_delete'),

]