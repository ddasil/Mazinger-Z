from django.db import models

class ChartSong(models.Model):
    title = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    normalized_genre = models.CharField(max_length=255)

    class Meta:
        unique_together = ('title', 'artist', 'normalized_genre')

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.normalized_genre})"
