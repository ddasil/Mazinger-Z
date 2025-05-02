from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import JsonResponse
from accounts.forms import CustomUserChangeForm  # 사용자 정보 수정 폼
from django.core.files.base import ContentFile  # ✅ 이거 추가

@login_required
def mypage(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            if 'profile_picture' in request.FILES:
                user.profile_picture = request.FILES['profile_picture']
            user.save()
            messages.success(request, '프로필이 성공적으로 업데이트되었습니다.')
            return redirect('mypage')
        else:
            print("❌ form errors:", form.errors)
    else:
        form = CustomUserChangeForm(instance=user)

    return render(request, 'mypage.html', {'form': form, 'user': user})



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
