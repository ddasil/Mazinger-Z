# accounts/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import CustomUser

# ✅ 선택 가능한 프로필 이미지 목록 (static/images/profiles/ 디렉토리 기준)
PROFILE_CHOICES = [
    ("profile1.png", "1번 이미지"),
    ("profile2.png", "2번 이미지"),
    ("profile3.png", "3번 이미지"),
    ("profile4.png", "4번 이미지"),
    ("profile5.png", "5번 이미지"),
]

class CustomUserCreationForm(UserCreationForm):
    birthday = forms.DateField(
        widget=forms.SelectDateWidget(years=range(1900, 2023)),
        required=True
    )
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        help_text="전화번호를 입력해주세요."
    )
    profile_picture = forms.ChoiceField(
        choices=PROFILE_CHOICES,
        required=False,
        label="프로필 사진 선택"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2', 'birthday', 'phone_number', 'profile_picture']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CustomUserChangeForm(UserChangeForm):
    nickname = forms.CharField(
        max_length=50,
        required=True,
        help_text="닉네임을 입력해주세요.",
        widget=forms.TextInput(attrs={'placeholder': '닉네임 입력'})
    )
    birthday = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '010-0000-0000'})
    )
    profile_picture = forms.ChoiceField(
        choices=PROFILE_CHOICES,
        required=False,
        label="프로필 사진 선택"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'nickname', 'birthday', 'phone_number', 'profile_picture']
        labels = {
            'username': 'ID',
            'nickname': '닉네임',
            'birthday': '생일',
            'phone_number': '전화번호',
            'profile_picture': '프로필 사진 선택',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields.pop('password')  # ✅ password 필드 제거


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'ID'
        self.fields['password'].label = 'PASSWORD'
