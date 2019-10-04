from allauth.account.forms import LoginForm, SignupForm
from django.urls import reverse_lazy
from django.views.generic import FormView


class LoginView(FormView):
    form_class = LoginForm
    template_name = 'account/login.html'
    success_url = ''


class SignUpView(FormView):
    form_class = SignupForm
    template_name = 'account/signup.html'
    success_url = reverse_lazy('index')
