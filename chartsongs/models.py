from django.db import models

class ChartSong(models.Model):
    # 🎵 곡 제목
    title = models.CharField(max_length=255)

    # 🎤 아티스트명
    artist = models.CharField(max_length=255)

    # 🏷️ 정규화된 장르 이름 (예: 힙합, 발라드 등)
    normalized_genre = models.CharField(max_length=255)

    # 📝 원본 가사 (오타 주의: lylics → lyrics로 수정 추천)
    lylics = models.TextField(blank=True, null=True)

    # 💬 감정 태그 3개 (예: ["슬픔", "위로", "비오는날"])
    emotion_tags = models.JSONField(blank=True, null=True)

    # 🧠 가사 기반 키워드 7개 추출 결과
    keywords = models.JSONField(blank=True, null=True)

    # 🆔 Genius에서 수집한 곡 고유 ID
    genius_id = models.IntegerField(unique=True, blank=True, null=True)

    # 🖼️ 앨범 커버 이미지 URL (벅스 등 백업 수단으로 수집 가능)
    album_cover_url = models.URLField(blank=True, null=True)

    # 📅 발매일
    release_date = models.DateField(blank=True, null=True)

    # ✅ 동일 곡 중복 저장 방지용 제약 조건
    class Meta:
        unique_together = ('title', 'artist', 'normalized_genre')

    # 🔁 어드민에서 표시될 문자열 형식
    def __str__(self):
        short_lyrics = self.lylics[:30] + ('...' if self.lylics and len(self.lylics) > 30 else '') if self.lylics else ''
        return f"{self.title} - {self.artist} ({self.normalized_genre}) / {short_lyrics}"
