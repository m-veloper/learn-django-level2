from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormView
from .models import Product
from .form import RegisterForm


# Create your views here.

class ProductList(ListView):
    model = Product
    template_name = 'product.html'
    context_object_name = 'product_list'

class ProductCreate(FormView):
    template_name = 'product_register.html'
    form_class = RegisterForm
    success_url = '/product/'

class ProductDetail(DetailView):
    template_name = 'product_detail.html'
    queryset = Product.objects.all()
    context_object_name = 'product'


