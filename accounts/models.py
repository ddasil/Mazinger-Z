from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # 필요한 필드 추가 가능 (예: 닉네임, 생년월일 등)
    pass
