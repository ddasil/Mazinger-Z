# accounts/forms.py
from django.contrib.auth.forms import UserCreationForm
from django import forms  # ✅ 2번에 필요한 추가 import
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password1', 'password2']

    # ✅ 2번: 폼 필드에 CSS 클래스 등 추가하고 싶을 때 (선택사항이지만 깔끔함)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'  # 예시로 form-control 클래스 추가
