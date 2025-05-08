from django.db import models
from django.conf import settings
# Create your models here.
class TaggedSong(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    lyrics = models.TextField()
    tags = models.JSONField(default=list)  # ["운동", "영화", "산책"]

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
class FavoriteSong(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    album_cover_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'title', 'artist')  # 중복 방지

    def __str__(self):
        return f"{self.user.username} - {self.title} by {self.artist}"