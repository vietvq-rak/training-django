import unicodedata

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, CreateView, ListView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy, reverse
from .forms import SignupForm
from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, render, redirect
from django.db.models import Count
from .models import EmailVerification, Product, Category


# HOME
class HomeView(TemplateView):
    template_name = 'store/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.annotate(product_count=Count('products'))
        return context

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


# EMAIL VERIFICATION
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


# CATEGORY
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'store/category_list.html'


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    fields = ['name']
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('category_list')


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    fields = ['name']
    template_name = 'store/category_form.html'
    success_url = reverse_lazy('category_list')


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'store/category_delete.html'
    success_url = reverse_lazy('category_list')


# PRODUCT
class ProductListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'store/product_list.html'

    def remove_accents(self, input_str):
        nfkd_form = unicodedata.normalize('NFKD', input_str)
        return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])

    def get_queryset(self):
        queryset = Product.objects.all()
        query = self.request.GET.get('query', '')
        category_id = self.request.GET.get('category', '')
        sort = self.request.GET.get('sort', '')

        if category_id and category_id != "all":
            queryset = queryset.filter(category_id=category_id)

        if query:
            query_normalized = self.remove_accents(query).lower()
            queryset = [p for p in queryset if query_normalized in self.remove_accents(p.name).lower()]

        if sort == "price_asc":
            queryset = queryset.order_by('price')
        elif sort == "price_desc":
            queryset = queryset.order_by('-price')
        elif sort == "name_asc":
            queryset = queryset.order_by('name')
        elif sort == "name_desc":
            queryset = queryset.order_by('-name')
        elif sort == "newest":
            queryset = queryset.order_by('-id')
        elif sort == "oldest":
            queryset = queryset.order_by('id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('query', '')
        context['category_id'] = self.request.GET.get('category', '')
        context['categories'] = Category.objects.annotate(product_count=Count('products'))
        context['sort'] = self.request.GET.get('sort', '')
        return context


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'store/product_detail.html'


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    fields = ['name', 'price', 'category', 'stock']
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    fields = ['name', 'price', 'category', 'stock']
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'store/product_delete.html'
    success_url = reverse_lazy('product_list')
