from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser  # 커스텀 유저 모델을 가져옵니다.

# CustomUser 모델을 Django Admin에 등록하고 관리할 수 있도록 설정합니다.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser  # CustomUser 모델을 지정

    # 어드민 페이지에서 표시할 필드 설정 (username, is_staff, is_active)
    list_display = ('username', 'nickname', 'is_staff', 'is_active')  # 사용자 이름, staff 여부, 활성화 상태 표시

    # 필터링 옵션 설정: 필터로 'is_staff', 'is_active', 'username'을 추가
    list_filter = ( 'username','is_staff', 'is_active')  # 'is_staff', 'is_active', 'username'을 필터로 사용

    # 사용자 정보 수정 시 표시할 필드 그룹 설정
    fieldsets = (
        (None, {'fields': ('username', 'password', 'nickname',)}),  # 기본 필드: username, password
        ('권한', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),  # 권한 관련 필드
    )

    # 사용자 추가 시 표시할 필드 그룹 설정
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # 'wide' 클래스 사용
            'fields': ('username', 'password1', 'password2', 'nickname', 'is_staff', 'is_active')  # 추가 시 사용할 필드
        }),
    )

    # 사용자 이름을 검색할 수 있도록 설정
    search_fields = ('username', 'nickname')  # 'username'으로 검색 가능

    # 어드민 페이지에서 기본적으로 정렬할 기준을 설정 (여기서는 'username' 기준으로 정렬)
    ordering = ('username',)
