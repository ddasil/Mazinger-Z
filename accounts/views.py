from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from .models import CustomUser
from django.contrib import messages # 아이디찾기
from django.contrib.auth import get_user_model # 비밀번호찾기
from django.http import HttpResponse # 비밀번호찾기
from django.contrib.auth.hashers import make_password # 비밀번호 재설정
from .forms import PasswordResetForm

def signup_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST,request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 회원가입 후 바로 로그인
            return redirect('main')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})


# 로그인뷰
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('main')  # 또는 '/'

    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})

# 로그아웃 뷰
def logout_view(request):
    logout(request)
    return redirect('main')


def check_nickname(request):
    nickname = request.GET.get('nickname')
    current_user_id = request.user.id
    exists = CustomUser.objects.exclude(pk=current_user_id).filter(nickname=nickname).exists()
    return JsonResponse({'duplicate': exists})

# 아이디찾기
def find_username(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        user = CustomUser.objects.filter(phone_number=phone).first()
        if user:
            return render(request, 'found_username.html', {'username': user.username})
        else:
            messages.error(request, '일치하는 사용자가 없습니다.')
    return render(request, 'find_username.html')

# 비밀번호찾기
def find_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        phone = request.POST.get('phone_number')
        try:
            user = CustomUser.objects.get(username=username, phone_number=phone)
            return redirect('reset_password', uid=user.username)
        except CustomUser.DoesNotExist:
            messages.error(request, '일치하는 사용자 정보가 없습니다.')
    return render(request, 'find_password.html')

def reset_password(request, uid):
    try:
        user = CustomUser.objects.get(username=uid)
    except CustomUser.DoesNotExist:
        messages.error(request, '유효하지 않은 접근입니다.')
        return redirect('find_password')

    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            new_pw = form.cleaned_data['new_password']
            user.password = make_password(new_pw)
            user.save()
            messages.success(request, '비밀번호가 재설정되었습니다.')
            return redirect('login')
        else:
            messages.error(request, '비밀번호가 일치하지 않습니다.')  # ❗ 안내문구
    else:
        form = PasswordResetForm()

    return render(request, 'reset_password.html', {'form': form, 'username': uid})

def check_username(request):
    username = request.GET.get('username')
    exists = CustomUser.objects.filter(username=username).exists()
    return JsonResponse({'available': not exists})

