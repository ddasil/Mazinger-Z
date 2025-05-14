from django.shortcuts import render, redirect
from .models import SupportPost, SupportReply
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404


def support_board_list(request):
    category = request.GET.get('category')
    posts = SupportPost.objects.filter(category=category).order_by('-created_at') if category else SupportPost.objects.all().order_by('-created_at')

    return render(request, 'board_list.html', {
        'posts': posts,
        'selected_category': category,
        'is_general': category == "general",
        'is_bug': category == "bug",
        'is_feature': category == "feature",
        'is_account': category == "account",
        'is_other': category == "other"
    })



@login_required
def support_board_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        message = request.POST.get('message')
        category = request.POST.get('category')

        SupportPost.objects.create(
            user=request.user,
            title=title,
            message=message,
            category=category
        )
        return render(request, 'board_create_success.html')
    return render(request, 'board_create.html')



def support_board_detail(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    reply = getattr(post, 'supportreply', None)
    return render(request, 'board_detail.html', {'post': post, 'reply': reply})

@user_passes_test(lambda u: u.is_staff)
def support_board_reply(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')
        SupportReply.objects.create(post=post, responder=request.user, reply_text=reply_text)
        return redirect('support_board_detail', pk=pk)
    return render(request, 'board_reply.html', {'post': post})


from django.http import HttpResponseForbidden

@login_required
def support_board_delete(request, pk):
    post = get_object_or_404(SupportPost, pk=pk)
    if post.user != request.user:
        return HttpResponseForbidden("본인 게시글만 삭제할 수 있습니다.")
    if request.method == 'POST':
        post.delete()
        return redirect('support_board_list')
    return render(request, 'board_delete_confirm.html', {'post': post})