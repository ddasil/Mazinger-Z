from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True,
        default='thumbnails/default.png'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def like_count(self):  # ✅ post_likes는 PostLike의 related_name
        return self.post_likes.count()
    like_count.fget.short_description = '좋아요 수'  # ✅ admin list_display용


class PostSong(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='songs')
    song_title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    album_cover_url = models.URLField()
    release_date = models.DateField()


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class PostLike(models.Model):  # ✅ 명확한 모델명
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = '게시글 좋아요'
        verbose_name_plural = '게시글 좋아요 목록'

    def __str__(self):
        return f"{self.user.nickname} → {self.post.title}"
