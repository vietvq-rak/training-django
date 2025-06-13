from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False)
    is_verified = models.BooleanField(default=False)


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(blank=False, null=False, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
