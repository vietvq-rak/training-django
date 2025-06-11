from captcha.fields import CaptchaField
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class CustomLoginForm(AuthenticationForm):
    captcha = CaptchaField()


def validate_username_custom(value):
    pattern = r'^[a-zA-Z][a-zA-Z0-9]{4,19}$'
    if not re.match(pattern, value):
        raise ValidationError("Username phải bắt đầu bằng chữ cái và có 5–20 ký tự chữ cái hoặc số.")


class SignupForm(UserCreationForm):
    error_messages = {
        'password_mismatch': "Mật khẩu không khớp.",
    }
    email = forms.EmailField(required=True)
    captcha = CaptchaField()
    username = forms.CharField(
        min_length=5,
        validators=[validate_username_custom],
        help_text="Username phải bắt đầu bằng chữ cái và có ít nhất 5 ký tự chữ cái hoặc số.",
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'captcha']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].help_text = (
            "Mật khẩu phải có ít nhất 8 ký tự, chứa ít nhất 1 chữ in hoa, "
            "1 ký tự đặc biệt và cả chữ cái và số."
        )
        self.fields['password1'].error_messages = {
            'required': 'Vui lòng nhập mật khẩu.',
        }

        self.fields['password2'].error_messages = {
            'required': 'Vui lòng xác nhận mật khẩu.',
        }
        self.fields['password2'].help_text = (
            "Nhập lại mật khẩu để xác nhận."
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email này đã được sử dụng cho tài khoản khác.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username này đã được sử dụng.")
        return username


class CustomPasswordChangeForm(PasswordChangeForm):
    error_messages = {
        'password_mismatch': "Mật khẩu mới không khớp.",
        'password_incorrect': "Mật khẩu cũ không đúng.",
    }
    captcha = CaptchaField(label="Mã xác nhận")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['old_password'].label = "Mật khẩu cũ"

        self.fields['new_password1'].label = "Mật khẩu mới"

        self.fields['new_password2'].label = "Xác nhận mật khẩu mới"
