from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import JsonResponse
from accounts.forms import CustomUserChangeForm  # 사용자 정보 수정 폼
<<<<<<< HEAD
from django.core.files.base import ContentFile  # ✅ 이거 추가
=======
from django.db import IntegrityError  # DB 오류 처리를 위해 import

>>>>>>> dayoung

@login_required
def mypage(request):
    user = request.user  # 현재 로그인한 사용자 객체

    if request.method == 'POST':
<<<<<<< HEAD
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

=======
        # 사용자 입력 기반으로 폼 생성 (현재 사용자 정보를 instance로 전달)
        form = CustomUserChangeForm(request.POST, instance=user)

        # 폼 유효성 검사
        if form.is_valid():
            try:
                # 유효하면 저장 시도
                form.save()
                messages.success(request, '프로필이 성공적으로 저장되었습니다.')
                return redirect('mypage')  # 저장 후 리다이렉트
            except IntegrityError:
                # DB에서 unique 제약 위반 발생 시 닉네임 중복 에러 처리
                form.add_error('nickname', '이미 존재하는 닉네임입니다.')
        else:
            # 폼이 유효하지 않으면 메시지 출력 (예: 형식 오류)
            messages.error(request, '입력값을 다시 확인해주세요.')

        # 폼에 에러가 있을 경우 다시 렌더링해서 오류 표시
        return render(request, 'mypage.html', {'form': form})

    else:
        # GET 요청 시 현재 사용자 정보를 가진 폼 생성
        form = CustomUserChangeForm(instance=user)
        return render(request, 'mypage.html', {'form': form})
>>>>>>> dayoung


@login_required
def verify_password(request):
    """
    JS fetch 요청을 통해 비밀번호 검증하는 뷰.
    사용자가 비밀번호 입력 시 서버에서 인증 확인 후 결과 반환.
    """
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        password = data.get('password')

        # 사용자 인증 시도
        user = authenticate(username=request.user.username, password=password)
        if user:
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False})
    return JsonResponse({'success': False}, status=400)
