# 작성한 가사들 데이터에 저장
from django.contrib import admin
from .models import GeneratedLyrics

admin.site.register(GeneratedLyrics)
