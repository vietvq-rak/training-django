# store/validators.py
from django.core.exceptions import ValidationError
import re


class StrongPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 chữ cái viết hoa.")
        if not re.search(r'[\W_]', password):
            raise ValidationError("Mật khẩu phải có ít nhất 1 ký tự đặc biệt.")
        if not re.search(r'[a-zA-Z]', password) or not re.search(r'[0-9]', password):
            raise ValidationError("Mật khẩu phải chứa cả chữ cái và chữ số.")
        if len(password) < 8:
            raise ValidationError("Mật khẩu phải có ít nhất 8 ký tự.")
    def get_help_text(self):
        return (
            "Mật khẩu phải có ít nhất 1 ký tự đặc biệt, 1 ký tự viết hoa, có cả chữ và số"
        )
