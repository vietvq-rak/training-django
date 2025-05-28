from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView, TemplateView
from django.urls import reverse_lazy

from .forms import SearchForm
from .models import Product, Customer, Order


class HomeView(TemplateView):
    template_name = 'store/home.html'


# Product Views

class ProductListView(ListView):
    model = Product
    template_name = 'store/product_list.html'


class ProductDetailView(DetailView):
    model = Product
    template_name = 'store/product_detail.html'


class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'price']
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'price']
    template_name = 'store/product_form.html'
    success_url = reverse_lazy('product_list')


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'store/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')


class ProductSearchView(FormView):
    template_name = 'store/product_search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        query = self.request.GET.get('query')
        results = None
        if query:
            results = Product.objects.filter(name__icontains=query)
        return self.render_to_response({
            'form': form,
            'query': query,
            'results': results,
        })



# Customer Views
class CustomerListView(ListView):
    model = Customer
    template_name = 'store/customer_list.html'


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'store/customer_detail.html'


class CustomerCreateView(CreateView):
    model = Customer
    fields = ['name', 'email']
    template_name = 'store/customer_form.html'
    success_url = reverse_lazy('customer_list')


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ['name', 'email']
    template_name = 'store/customer_form.html'
    success_url = reverse_lazy('customer_list')


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'store/customer_confirm_delete.html'
    success_url = reverse_lazy('customer_list')


class CustomerSearchView(FormView):
    template_name = 'store/customer_search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        query = self.request.GET.get('query')
        results = None
        if query:
            results = Customer.objects.filter(name__icontains=query)
        return self.render_to_response({
            'form': form,
            'query': query,
            'results': results,
        })



# Order Views
class OrderListView(ListView):
    model = Order
    template_name = 'store/order_list.html'


class OrderDetailView(DetailView):
    model = Order
    template_name = 'store/order_detail.html'


class OrderCreateView(CreateView):
    model = Order
    fields = ['customer', 'products']
    template_name = 'store/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderUpdateView(UpdateView):
    model = Order
    fields = ['customer', 'products']
    template_name = 'store/order_form.html'
    success_url = reverse_lazy('order_list')


class OrderDeleteView(DeleteView):
    model = Order
    template_name = 'store/order_confirm_delete.html'
    success_url = reverse_lazy('order_list')


class OrderSearchView(FormView):
    template_name = 'store/order_search.html'
    form_class = SearchForm

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        query = self.request.GET.get('query')
        results = None
        if query:
            results = Order.objects.filter(customer__name__icontains=query)
        return self.render_to_response({
            'form': form,
            'query': query,
            'results': results,
        })
