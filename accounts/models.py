import random
import string
from django.contrib.auth.models import AbstractUser
from django.db import models

def generate_random_nickname(length=8):
    # 랜덤한 문자열로 닉네임 생성 (알파벳과 숫자 혼합)
    letters_and_digits = string.ascii_letters + string.digits
    return ''.join(random.choice(letters_and_digits) for i in range(length))

class CustomUser(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True, blank=True, null=True)  # 닉네임은 자동 생성
    birthday = models.DateField(null=True, blank=True)  # 생일 필드 추가
    phone_number = models.CharField(max_length=15, blank=True, null=True)  # 전화번호 필드 추가
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # 프로필 사진 필드 추가

    def save(self, *args, **kwargs):
        if not self.nickname:  # 만약 nickname이 비어있다면
            self.nickname = generate_random_nickname()  # 랜덤으로 닉네임 생성
        super().save(*args, **kwargs)  # 기존 save 메서드 호출

    def __str__(self):
        return self.username  # 사용자 이름을 반환

