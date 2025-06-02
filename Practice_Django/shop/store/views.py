import json

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
)
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Category, Product, Order, OrderItem
from .forms import OrderForm, OrderItemForm, SignupForm
from django.contrib.auth.models import Group


# HOME
class HomeView(TemplateView):
    template_name = 'store/home.html'


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


# ORDER

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'store/order_list.html'

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Order.objects.all()
        else:
            return Order.objects.filter(customer=user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'store/order_detail.html'

    def get_object(self, queryset=None):
        order = super().get_object(queryset)
        user = self.request.user

        if user.is_superuser:
            return order

        if order.customer == user:
            return order

        raise PermissionDenied("Bạn không có quyền xem order này.")


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'store/order_form.html'

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderUpdateView(LoginRequiredMixin, UpdateView):
    model = Order
    form_class = OrderForm
    template_name = 'store/order_form.html'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.is_active:
            return Order.objects.filter(customer=self.request.user)

    def get_success_url(self):
        return reverse('order_detail', kwargs={'pk': self.object.pk})


class OrderDeleteView(LoginRequiredMixin, DeleteView):
    model = Order
    template_name = 'store/order_delete.html'
    success_url = reverse_lazy('order_list')

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        elif self.request.user.is_active:
            return Order.objects.filter(customer=self.request.user)


# ORDER ITEM
class OrderItemCreateView(LoginRequiredMixin, CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'store/orderitem_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.order = get_object_or_404(Order, pk=self.kwargs['order_id'])
        if not (request.user.is_superuser or self.order.customer == request.user):
            raise PermissionDenied("Bạn không có quyền thêm sản phẩm vào đơn này.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        item = form.save(commit=False)
        item.order = self.order
        item.price = item.product.price
        item.save()
        return redirect('order_detail', pk=self.order.pk)


class OrderItemUpdateView(LoginRequiredMixin, UpdateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name = 'store/orderitem_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.item = self.get_object()
        order = self.item.order
        if not (request.user.is_superuser or order.customer == request.user):
            raise PermissionDenied("Bạn không có quyền chỉnh sửa sản phẩm của đơn này.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        item = form.save(commit=False)
        item.price = item.product.price
        item.save()
        return redirect('order_detail', pk=item.order.pk)


class OrderItemDeleteView(LoginRequiredMixin, DeleteView):
    model = OrderItem
    template_name = 'store/orderitem_delete.html'

    # def get_queryset(self):
    #     order_id = self.kwargs['order_id']
    #     return OrderItem.objects.filter(order__id=order_id, order__customer=self.request.user)
    def dispatch(self, request, *args, **kwargs):
        self.item = self.get_object()
        order = self.item.order
        if not (request.user.is_superuser or order.customer == request.user):
            raise PermissionDenied("Bạn không có quyền chỉnh sửa sản phẩm của đơn này.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('order_detail', kwargs={'pk': self.object.order.pk})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()

        self.object.product.stock += self.object.quantity
        self.object.product.save()

        order_id = self.object.order.pk
        success_url = reverse('order_detail', kwargs={'pk': order_id})

        self.object.delete()
        return redirect(success_url)


# SIGNUP
class SignupView(CreateView):
    form_class = SignupForm
    template_name = 'store/signup.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        print("Form is valid, saving user...")
        user = form.save()
        customer_group = Group.objects.get(name='Customers')
        user.groups.add(customer_group)
        return super().form_valid(form)
