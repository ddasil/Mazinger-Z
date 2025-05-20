# ✅ views.py (mypage)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate
from django.http import JsonResponse
from accounts.forms import CustomUserChangeForm
from django.db import IntegrityError

from lyricsgen.models import GeneratedLyrics




@login_required
def mypage(request):
    user = request.user

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)

        if form.is_valid():
            try:
                # ✅ 폼으로부터 필드 수동 설정
                user.nickname = form.cleaned_data['nickname']
                user.birthday = form.cleaned_data['birthday']
                user.phone_number = form.cleaned_data['phone_number']
                user.profile_picture = form.cleaned_data['profile_picture']
                user.save()

                messages.success(request, '프로필이 성공적으로 저장되었습니다.')
                return redirect('mypage')
            except IntegrityError:
                form.add_error('nickname', '이미 존재하는 닉네임입니다.')
        else:
            messages.error(request, '입력값을 다시 확인해주세요.')

        return render(request, 'mypage.html', {'form': form})

    else:
        form = CustomUserChangeForm(instance=user)
        return render(request, 'mypage.html', {'form': form})
    
# 진섭추가
# ✅ 여기에 추가: 유저별 GeneratedLyrics 목록 JSON 반환
@login_required
def user_generated_lyrics(request):
    user = request.user
    lyrics_qs = GeneratedLyrics.objects.filter(user=user).order_by('-created_at')

    data = [
        {
            'id': lyric.id,
            'prompt': lyric.prompt,
            'style': lyric.style,
            'language': lyric.language,
            "created_at": lyric.created_at.strftime('%Y-%m-%d'),
        }
        for lyric in lyrics_qs
    ]
    return JsonResponse({'lyrics': data})

@login_required
def verify_password(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        password = data.get('password')
        user = authenticate(username=request.user.username, password=password)
        return JsonResponse({'success': bool(user)})
    return JsonResponse({'success': False}, status=400)
