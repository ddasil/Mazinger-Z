from django.contrib import admin
from .models import Post, PostSong, Comment, PostLike, PostScrap


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'like_count', 'scrap_count')
    list_display_links = ('id', 'title')
    readonly_fields = ('like_count', 'scrap_count', 'scrap_users_display')

    def scrap_users_display(self, obj):
        return ", ".join(scrap.user.username for scrap in obj.scrap_set.all())
    scrap_users_display.short_description = "스크랩한 사용자"


@admin.register(PostScrap)
class PostScrapAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)


@admin.register(PostLike)
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'created_at')
    list_filter = ('created_at',)


@admin.register(PostSong)
class PostSongAdmin(admin.ModelAdmin):
    list_display = ('post', 'song_title', 'artist', 'release_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'user', 'text', 'created_at')
