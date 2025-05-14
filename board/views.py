# board/views.py

from django.shortcuts import render
from .models import Post, PostLike
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import PostForm

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
    post = get_object_or_404(Post, pk=pk)

    # ✅ 로그인한 사용자가 이 게시글을 좋아요 했는지 미리 계산해서 넘기기
    liked = False
    if request.user.is_authenticated:
        liked = PostLike.objects.filter(post=post, user=request.user).exists()

    return render(request, 'post_detail.html', {
        'post': post,
        'liked': liked,  # ✅ 템플릿에서 사용
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
