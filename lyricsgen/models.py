
from django.db import models
from django.contrib.auth import get_user_model  # 🔹 유저 모델 가져오기
from django.contrib.auth import get_user_model
User = get_user_model()

class GeneratedLyrics(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)  
    prompt = models.CharField(max_length=255)
    style = models.CharField(max_length=50)

    # 🔽 기존에는 title이 없어서 제목을 DB에 저장할 수 없었음
    # lyrics = models.TextField()
    # 🔽 아래처럼 title 필드를 새로 추가함
    title = models.CharField(max_length=255, null=True, blank=True)  # ✅ GPT가 추출한 제목 저장용 필드

    lyrics = models.TextField()  # ✅ 기존과 동일
    language = models.CharField(max_length=20, default='none')
    image_file = models.ImageField(upload_to='album_covers/')  # 로컬 이미지 파일 경로
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField()
    temp_user_id = models.CharField(max_length=100, null=True, blank=True)  # ✅ 비회원용 세션 ID 저장

    def __str__(self):
        return f"{self.prompt} ({self.style})"