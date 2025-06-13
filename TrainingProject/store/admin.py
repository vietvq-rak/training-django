from django.contrib import admin
from .models import EmailVerification, Category, Product

# Register your models here.

admin.site.register(EmailVerification)
admin.site.register(Category)
admin.site.register(Product)
