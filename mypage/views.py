from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import CustomUserChangeForm  # 사용자 정보 수정 폼
from accounts.models import CustomUser  # 사용자 모델

@login_required
def mypage(request):
    user = request.user  # 로그인한 사용자 정보

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, request.FILES, instance=user)  # 폼을 받아서 사용자 정보 수정
        if form.is_valid():
            form.save()  # 저장
            return redirect('mypage')  # 마이페이지로 리디렉션
    else:
        form = CustomUserChangeForm(instance=user)  # 기존 사용자 정보로 폼 초기화

    return render(request, 'mypage.html', {'form': form})
