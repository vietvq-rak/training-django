from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    stock = models.PositiveIntegerField(blank=False, null=False, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    date = models.DateTimeField(auto_now=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.customer.username}"

    def get_total(self):
        return sum(item.get_total_price() for item in self.orderitem_set.all())

    def delete(self, *args, **kwargs):
        for item in self.orderitem_set.all():
            item.product.stock += item.quantity
            item.product.save()
        super().delete(*args, **kwargs)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_total_price(self):
        return self.quantity * self.price

    def save(self, *args, **kwargs):
        if self.pk is None:
            if self.product.stock < self.quantity:
                raise ValueError("Số lượng trong kho không đủ!")
            self.product.stock -= self.quantity
            self.product.save()
        else:
            old_item = OrderItem.objects.get(pk=self.pk)
            qty_diff = self.quantity - old_item.quantity

            if qty_diff > 0:
                if self.product.stock < qty_diff:
                    raise ValueError("Số lượng trong kho không đủ để tăng!")
                self.product.stock -= qty_diff
            elif qty_diff < 0:
                self.product.stock += abs(qty_diff)

            self.product.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.product.stock += self.quantity
        self.product.save()
        super().delete(*args, **kwargs)