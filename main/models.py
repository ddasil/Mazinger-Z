from django.db import models
from django.conf import settings
from django.utils import timezone

class Lovelist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    cover_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'title', 'artist')

    def __str__(self):
        return f"{self.user} - {self.title} by {self.artist}"



# 인기 태그 검색 저장 모델
class TagSearchLog(models.Model):
    tag = models.CharField(max_length=100)
    searched_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.tag