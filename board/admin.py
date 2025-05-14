from django.contrib import admin
from .models import Post, PostSong, Comment, PostLike  # ✅ Like → PostLike로 변경


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'like_count')  # ✅ 좋아요 수 표시
    readonly_fields = ('like_count',)

    def like_count(self, obj):
        return obj.post_likes.count()
    like_count.short_description = '좋아요 수'


@admin.register(PostSong)
class PostSongAdmin(admin.ModelAdmin):
    list_display = ('post', 'song_title', 'artist', 'release_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text', 'created_at')


@admin.register(PostLike)  # ✅ 새로운 PostLike 모델 등록
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)
