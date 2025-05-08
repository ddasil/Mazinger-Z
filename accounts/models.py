import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models

def generate_random_nickname(length=8):
    # 랜덤한 문자열로 닉네임 생성 (알파벳과 숫자 혼합)
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for _ in range(length))

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True, blank=True, null=True)  # 닉네임은 자동 생성
    birthday = models.DateField(null=True, blank=True)  # 생일 필드 추가
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 전화번호 필드 추가

    # ✅ 선택된 이미지 파일명만 저장 (업로드 아님)
    profile_picture = models.CharField(
        max_length=100,
        choices=[
            ('profile1.png', '프로필1'),
            ('profile2.png', '프로필2'),
            ('profile3.png', '프로필3'),
            ('profile4.png', '프로필4'),
            ('profile5.png', '프로필5'),
        ],
        default='profile1.png'
    )

    def save(self, *args, **kwargs):
        # 닉네임이 없으면 자동 생성
        if not self.nickname:
            self.nickname = generate_random_nickname()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
