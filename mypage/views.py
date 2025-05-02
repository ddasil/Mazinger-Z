from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import JsonResponse
from accounts.forms import CustomUserChangeForm  # 사용자 정보 수정 폼

@login_required
def mypage(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage')
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'mypage.html', {
        'form': form,
        'user': user,  # template에서 {{ user.nickname }} 등으로 쓸 수 있게 전달
    })

@login_required
def verify_password(request):
    """
    JS에서 fetch로 비밀번호 확인용 뷰.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        password = data.get('password')
        user = authenticate(username=request.user.username, password=password)
        if user:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False}, status=400)
