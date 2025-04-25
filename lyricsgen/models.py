
from django.db import models
from django.contrib.auth import get_user_model  # 🔹 유저 모델 가져오기

class GeneratedLyrics(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)  
    prompt = models.CharField(max_length=255)
    style = models.CharField(max_length=50)
    lyrics = models.TextField()
    language = models.CharField(max_length=20, default='none')
    image_file = models.ImageField(upload_to='album_covers/')  # 로컬 이미지 파일 경로
    created_at = models.DateTimeField(auto_now_add=True)
    duration = models.FloatField()

    def __str__(self):
        return f"{self.prompt} ({self.style})"
