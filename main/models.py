from django.db import models
from django.conf import settings

class Lovelist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    cover_url = models.URLField(blank=True, null=True)

    is_liked = models.BooleanField(default=True)  # ✅ 좋아요 상태만 표시

    class Meta:
        unique_together = ('user', 'title', 'artist')

    def __str__(self):
        return f"{self.user} - {self.title} by {self.artist}"