from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from .form import RegisterForm

# Create your views here.

class OrderCreate(FormView):
    form_class = RegisterForm
    success_url = '/product/'

    def form_invalid(self, form):
        return redirect('/product/' + str(form.product))

    def get_form_kwargs(self, **kwargs):
        kw = super(OrderCreate, self).get_form_kwargs(**kwargs)
        kw.update({
            'request': self.request
        })
        return kw