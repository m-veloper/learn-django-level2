from django.shortcuts import render
from django.views.generic.edit import FormView
from .form import RegisterForm, LoginForm

# Create your views here.

def index(request):
    return render(request, 'index.html', {'email': request.session.get('user')})

class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = '/'

class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = '/'

    def form_valid(self, form):
        self.request.session['user'] = form.email

        return super().form_valid(form)