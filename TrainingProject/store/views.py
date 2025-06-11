from django.views import View
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy, reverse
from .forms import SignupForm
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect

from .models import EmailVerification


# HOME
class HomeView(TemplateView):
    template_name = 'store/home.html'

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and not (user.is_staff or user.is_superuser):
            try:
                verification = EmailVerification.objects.get(user=user)
                if not verification.is_verified:
                    return redirect('verify_reminder')
            except EmailVerification.DoesNotExist:
                return redirect('home')
        return super().dispatch(request, *args, **kwargs)


# SIGNUP
class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'store/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        print("Form is valid, saving user...")
        user = form.save()

        verification = EmailVerification.objects.create(user=user)

        # Tạo link xác thực tuyệt đối
        verify_url = self.request.build_absolute_uri(
            reverse('email_verify', kwargs={'token': str(verification.token)})
        )
        subject = 'Kích hoạt tài khoản của bạn'
        message = f"""
        Chào {user.username},

        Cảm ơn bạn đã đăng ký tài khoản.

        Vui lòng click vào link dưới đây để kích hoạt tài khoản của bạn:

        {verify_url}

        Nếu bạn không đăng ký, hãy bỏ qua email này.

        Trân trọng,
        """

        send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email])
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Form is invalid, errors:", form.errors)
        return super().form_invalid(form)


class EmailVerifyView(View):
    def get(self, request, token):
        verification = get_object_or_404(EmailVerification, token=token)

        if not verification.is_verified:
            verification.is_verified = True
            verification.save()

            user = verification.user
            user.save()

            customer_group = Group.objects.get(name='Customers')
            user.groups.add(customer_group)

            return render(request, 'store/email_verified.html')

        else:
            return render(request, 'store/email_already_verified.html')


class VerifyReminderView(TemplateView):
    template_name = 'store/verify_reminder.html'