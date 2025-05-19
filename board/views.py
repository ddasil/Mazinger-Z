from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.contrib import messages
from .models import Post, PostLike, Comment, PostScrap, PostRecentView
from .forms import PostForm, CommentForm
from django.core.paginator import Paginator
from django.db.models import Q
from main.models import Lovelist
from django.views.decorators.http import require_POST

# ✅ 게시글 목록
def post_list(request):
    q = request.GET.get('q', '')
    post_queryset = Post.objects.all().order_by('-created_at')

    if q:
        post_queryset = post_queryset.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )

    paginator = Paginator(post_queryset, 4)
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    user = request.user
    scrapped_posts, recent_posts, my_posts = [], [], []

    if user.is_authenticated:
        scrapped_posts = Post.objects.filter(scrap_set__user=user).order_by('-scrap_set__created_at')[:10]
        my_posts = Post.objects.filter(user=user).order_by('-created_at')[:10]
        recent_ids = PostRecentView.objects.filter(user=user).values_list('post_id', flat=True)[:10]
        recent_posts = Post.objects.filter(id__in=recent_ids)
    else:
        recent_ids = request.session.get('recent_posts', [])
        recent_posts = Post.objects.filter(id__in=recent_ids) if recent_ids else []

    return render(request, 'post_list.html', {
        'posts': posts,
        'scrapped_posts': scrapped_posts,
        'recent_posts': recent_posts,
        'my_posts': my_posts,
        'query': q,
    })


# ✅ 게시글 작성
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            # ✅ 선택한 곡 ID 연결
            selected_ids = request.POST.getlist('songs')
            post.lovelist_songs.set(Lovelist.objects.filter(id__in=selected_ids))
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm()

    lovelist = Lovelist.objects.filter(user=request.user, is_liked=True)
    return render(request, 'post_form.html', {
        'form': form,
        'lovelist': lovelist,
        'selected_songs': []
    })


# ✅ 게시글 상세
def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)

    # ✅ 최근 본 처리
    if request.user.is_authenticated:
        PostRecentView.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={'viewed_at': timezone.now()}
        )
    else:
        recent = request.session.get('recent_posts', [])
        if pk not in recent:
            recent = [pk] + recent[:2]
            request.session['recent_posts'] = recent

    # ✅ 좋아요 상태
    liked = post.post_likes.filter(user=request.user).exists() if request.user.is_authenticated else False

    # ✅ 댓글 처리
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()

    # ✅ 선택된 곡
    selected_songs = post.lovelist_songs.all()

    return render(request, 'post_detail.html', {
        'post': post,
        'liked': liked,
        'comment_form': form,
        'selected_songs': selected_songs,
    })

# ✅ 게시글 수정
@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save()
            selected_ids = request.POST.getlist('songs')
            post.lovelist_songs.set(Lovelist.objects.filter(id__in=selected_ids))
            return redirect('post_detail', pk=post.pk)
    else:
        form = PostForm(instance=post)

    selected_songs = post.lovelist_songs.all()
    selected_song_ids = [str(song.id) for song in selected_songs]  # ✅ 이 줄이 핵심!

    user_lovelist = list(Lovelist.objects.filter(user=request.user))
    missing_songs = [s for s in selected_songs if s not in user_lovelist]
    lovelist = user_lovelist + missing_songs

    return render(request, 'post_form.html', {
        'form': form,
        'lovelist': lovelist,
        'selected_songs': selected_songs,
        'selected_song_ids': selected_song_ids,  # ✅ 이 줄도 중요!
    })

# ✅ 게시글 삭제
@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    if request.method == 'POST':
        post.delete()
        messages.success(request, '게시글이 삭제되었습니다.')
        return redirect('post_list')
    return render(request, 'post_confirm_delete.html', {'post': post})


# ✅ 좋아요 토글
@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like = PostLike.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
    else:
        PostLike.objects.create(post=post, user=request.user)
    return redirect('post_detail', pk=pk)


# ✅ 댓글 대댓글 작성
@login_required
def comment_reply(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.user = request.user
            reply.post = post
            reply.parent = parent_comment
            reply.save()

    return redirect('post_detail', pk=post.pk)


# ✅ 스크랩 토글
@login_required
def scrap_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    user = request.user
    scrap = PostScrap.objects.filter(post=post, user=user).first()
    if scrap:
        scrap.delete()
    else:
        PostScrap.objects.create(post=post, user=user)
    return redirect(request.META.get('HTTP_REFERER', '/'))


# ✅ 좋아요한 곡 추가/삭제
@require_POST
@login_required
def toggle_lovelist(request):
    title = request.POST['title']
    artist = request.POST['artist']
    cover_url = request.POST.get('cover_url')

    song, created = Lovelist.objects.get_or_create(
        user=request.user,
        title=title,
        artist=artist,
        defaults={'cover_url': cover_url, 'is_liked': True}
    )

    print("🔁 toggle_lovelist 실행됨")
    print("   → song:", song.title)
    print("   → created:", created)

    if not created:
        song.is_liked = not song.is_liked
        song.save()
        print("   → 상태 변경됨: is_liked =", song.is_liked)
    else:
        print("   → 신규 생성됨: 기본 좋아요 상태 유지")

    return redirect(request.META.get('HTTP_REFERER', '/'))

