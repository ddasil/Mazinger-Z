# board/views.py

from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, PostLike, Comment
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm, CommentForm

# 🎯 게시글 목록을 보여주는 뷰
def post_list(request):
    # 모든 게시글을 최신순으로 가져옴
    posts = Post.objects.all().order_by('-created_at')

    # 현재 templates 폴더 구조가: board/templates/post_list.html 이므로 템플릿 경로를 직접 문자열로 명시해줘야 함
    return render(request, 'post_list.html', {'posts': posts})

# 🎯 게시글 작성 뷰 (로그인된 사용자만 접근 가능)
@login_required
def post_create(request):
    if request.method == "POST":
        # 사용자가 입력한 값과 업로드 파일을 함께 넘겨줌
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)  # 저장을 잠깐 멈추고
            post.user = request.user       # 현재 로그인한 사용자를 작성자로 지정
            post.save()                    # 이제 저장
            return redirect('post_list')   # 글 작성 후 게시판 목록으로 이동
    else:
        form = PostForm()  # 빈 폼 전달

    return render(request, 'post_form.html', {'form': form})

def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    liked = post.post_likes.filter(user=request.user).exists() if request.user.is_authenticated else False

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


@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like = PostLike.objects.filter(post=post, user=request.user).first()

    if like:
        like.delete()
    else:
        PostLike.objects.create(post=post, user=request.user)

    return redirect('post_detail', pk=pk)

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