from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm

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

