from django.shortcuts import render
from django.views.generic.edit import FormView
from .form import RegisterForm, LoginForm

# Create your views here.

def index(request):
    return render(request, 'index.html')

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = '/'

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/'