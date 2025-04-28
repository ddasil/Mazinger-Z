from django.http import HttpResponse

# 홈 페이지 뷰
def home(request):
    if request.user.is_authenticated:
        # 로그인한 사용자일 경우 닉네임 출력
        nickname = request.user.nickname
        return HttpResponse(f"안녕하세요, {nickname}님!")  # 닉네임을 포함하여 응답
    else:
        # 로그인하지 않은 사용자에게는 안내 메시지
        return HttpResponse("로그인 후 사용 가능합니다.")
