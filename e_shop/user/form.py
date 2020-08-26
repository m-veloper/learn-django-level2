from django import forms
from .models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(
        error_messages={
            'required': '이메일을 입력해주세요.'
        },
        max_length=100, label='이메일'
    )
    password = forms.CharField(
        error_messages={
            'required': '비밀번호을 입력해주세요.'
        },
        widget=forms.PasswordInput, label='비밀번호'
    )
    re_password = forms.CharField(
        error_messages={
            'required': '비밀번호을 입력해주세요.'
        },
        widget=forms.PasswordInput, label='비밀번호 확인'
    )

    def clean(self):
        cleand_data = super().clean()
        email = cleand_data.get('email')
        password = cleand_data.get('password')
        re_password = cleand_data.get('re_password')

        if password and re_password:
            if password != re_password:
                self.add_error('password', '비밀번호가 서로 다릅니다.')
                self.add_error('re_password', '비밀번호가 서로 다릅니다.')
            else:
                user = User(
                    email = email,
                    password = password
                )
                user.save()
