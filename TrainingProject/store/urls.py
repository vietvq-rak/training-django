from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

from .forms import CustomLoginForm, CustomPasswordChangeForm


urlpatterns = [

    # Signup
    path('accounts/login/',
         auth_views.LoginView.as_view(template_name='store/login.html', authentication_form=CustomLoginForm),
         name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('accounts/signup/', views.SignupView.as_view(template_name='store/signup.html'), name='signup'),
    # Password change
    path('password-change/', auth_views.PasswordChangeView.as_view(form_class=CustomPasswordChangeForm, template_name='store/password_change.html', success_url='/password-change/done/'), name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='store/password_change_done.html'), name='password_change_done'),
    # Email verification
    path('verify-email/<uuid:token>/', views.EmailVerifyView.as_view(), name='email_verify'),
    path('verify-reminder/', views.VerifyReminderView.as_view(), name='verify_reminder'),
    # Homes
    path('', views.HomeView.as_view(), name='home'),
    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    # Products
    path('products/', views.ProductListView.as_view(), name='product_list'),
    path('products/add/', views.ProductCreateView.as_view(), name='product_create'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('products/<int:pk>/edit/', views.ProductUpdateView.as_view(), name='product_update'),
    path('products/<int:pk>/delete/', views.ProductDeleteView.as_view(), name='product_delete'),

]

