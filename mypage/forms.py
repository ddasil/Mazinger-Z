class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'nickname', 'birthday', 'phone_number', 'profile_picture')
        labels = {
            'username': 'ID',
            'nickname': '닉네임',
            'birthday': '생일',
            'phone_number': '전화번호',
            'profile_picture': '프로필 사진',
        }
        help_texts = {
            'nickname': '닉네임을 입력해주세요.',
            'birthday': '예: 1990-01-01',
        }
        widgets = {
            'nickname': forms.TextInput(attrs={'placeholder': '닉네임 입력'}),
            'birthday': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '010-0000-0000'}),
        }
