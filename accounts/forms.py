# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms  # ✅ 2번에 필요한 추가 import
from .models import CustomUser
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.forms import AuthenticationForm


class CustomUserCreationForm(UserCreationForm):
    # 추가된 필드: 생일과 전화번호
    birthday = forms.DateField(widget=forms.SelectDateWidget(years=range(1900, 2023)), required=True)
    phone_number = forms.CharField(max_length=15, required=True, help_text="전화번호를 입력해주세요.")
    profile_picture = forms.ImageField(required=False)  # 프로필 사진 필드 추가

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'birthday', 'phone_number', 'profile_picture']

    # ✅ 2번: 폼 필드에 CSS 클래스 등 추가하고 싶을 때 (선택사항이지만 깔끔함)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # 예시로 form-control 클래스 추가

class CustomUserChangeForm(UserChangeForm):
    # 이 폼에서는 사용자의 기본 정보(닉네임, 전화번호, 프로필 사진 등)를 변경할 수 있습니다.
    
    # 프로필 사진 필드를 추가하려면 ImageField를 정의할 수 있습니다.
    profile_picture = forms.ImageField(required=False)
    nickname = forms.CharField(max_length=50, required=True, help_text="닉네임을 입력해주세요.")  # 닉네임 필드 추가
    
    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'birthday', 'phone_number', 'profile_picture']


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ID'
        self.fields['password'].label = 'PASSWORD'