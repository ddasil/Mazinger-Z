from django.db import models
from django.conf import settings  # 🔄 변경된 부분

class UserSong(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # 🔄 변경된 부분
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    top3_emotions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.user.username})"

class Song(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    top2_emotions = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.artist}"
