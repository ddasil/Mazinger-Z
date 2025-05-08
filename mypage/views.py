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
        nickname = request.POST.get('nickname')
        birthday = request.POST.get('birthday')
        phone_number = request.POST.get('phone_number')
        profile_picture = request.POST.get('profile_picture')

        # ✅ 직접 저장
        user.nickname = nickname
        user.birthday = birthday if birthday else None
        user.phone_number = phone_number
        user.profile_picture = profile_picture
        user.save()

        messages.success(request, '프로필이 성공적으로 저장되었습니다.')
        return redirect('mypage')

    return render(request, 'mypage.html', {'user': user})



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
