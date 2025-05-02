from django.db import models

class ChartSong(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    normalized_genre = models.CharField(max_length=255)
    lylics = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('title', 'artist', 'normalized_genre')

    def __str__(self):
        short_lyrics = (self.lylics[:30] + '...') if self.lylics and len(self.lylics) > 30 else self.lylics
        return f"{self.title} - {self.artist} ({self.normalized_genre}) / 가사: {self.lylics}"
