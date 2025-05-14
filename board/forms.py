# board/forms.py

from django import forms
from .models import Post

# 🎯 게시글 작성 폼 정의 (Post 모델 기반)
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'description', 'thumbnail']  # 사용자가 입력할 필드들

        # 폼 필드에 CSS 클래스와 placeholder 추가
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '제목 입력'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': '설명 입력'}),
        }
