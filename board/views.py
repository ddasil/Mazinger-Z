from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone

from .models import Post, PostLike, Comment, PostScrap, PostRecentView
from .forms import PostForm, CommentForm


# ✅ 게시글 목록 (사이드바 포함)
def post_list(request):
    posts = Post.objects.all().order_by('-created_at')

    user = request.user
    scrapped_posts = []
    recent_posts = []
    my_posts = []

    if user.is_authenticated:
        # 로그인 유저: DB에서 불러오기
        scrapped_posts = Post.objects.filter(scrap_set__user=user).order_by('-scrap_set__created_at')[:3]
        my_posts = Post.objects.filter(user=user).order_by('-created_at')[:3]
        recent_ids = PostRecentView.objects.filter(user=user).values_list('post_id', flat=True)[:3]
        recent_posts = Post.objects.filter(id__in=recent_ids)
    else:
        # 비로그인 유저: 세션에서 불러오기
        recent_ids = request.session.get('recent_posts', [])
        recent_posts = Post.objects.filter(id__in=recent_ids) if recent_ids else []

    return render(request, 'post_list.html', {
        'posts': posts,
        'scrapped_posts': scrapped_posts,
        'recent_posts': recent_posts,
        'my_posts': my_posts,
    })


# ✅ 게시글 작성
@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            return redirect('post_list')
    else:
        form = PostForm()
    return render(request, 'post_form.html', {'form': form})


# ✅ 게시글 상세 + 최근 본 처리
def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)

    # 최근 본 처리
    if request.user.is_authenticated:
        PostRecentView.objects.update_or_create(
            user=request.user,
            post=post,
            defaults={'viewed_at': timezone.now()}
        )
    else:
        recent = request.session.get('recent_posts', [])
        if pk not in recent:
            recent = [pk] + recent[:2]  # 최대 3개 유지
            request.session['recent_posts'] = recent

    # 좋아요 상태 확인
    liked = post.post_likes.filter(user=request.user).exists() if request.user.is_authenticated else False

    # 댓글 처리
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

    return render(request, 'post_detail.html', {
        'post': post,
        'liked': liked,
        'comment_form': form
    })


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


# ✅ 대댓글 작성
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
