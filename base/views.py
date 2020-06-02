from django.shortcuts import render, reverse
from django.views.generic import DetailView, CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from base.forms import RegisterForm
# from stories.models import Story


# Create your views here.
def home(request):
    return render(request, template_name="base/index.html")


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user'
    template_name = "base/profile.html"

    def get_object(self):
        return User.objects.get(username=self.kwargs['slug'])


class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = RegisterForm

    def get_success_url(self):
        return reverse('home')


# login view

class Login(LoginView):
    # security issues (may not be a problem rn)/redirect issues with this (don't have permissions on this site)
    # for more info:
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    redirect_authenticated_user = True


# def login(request):
#     form = LoginForm()
#     return render(request, "base/login.html", {'form': form})
