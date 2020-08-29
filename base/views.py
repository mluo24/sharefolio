from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import DetailView, CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from base.forms import RegisterForm, PlainUserForm, UserProfileForm
from base.models import UserProfile


def home(request):
    return render(request, template_name="base/index.html")


class UserProfileView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'pageuser'
    template_name = "base/profile.html"

    def get_object(self):
        return User.objects.get(username=self.kwargs['slug'])


class UserProfileEditView(LoginRequiredMixin, TemplateView):
    user_form_class = PlainUserForm
    profile_form_class = UserProfileForm
    template_name = 'base/update_profile.html'
    slug_field = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'user_form' not in context:
            context['user_form'] = self.user_form_class(instance=self.request.user)
        if 'profile_form' not in context:
            context['profile_form'] = self.profile_form_class(instance=self.request.user.userprofile)
        return context

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        post_data = request.POST or None
        user_form = self.user_form_class(post_data, instance=request.user)
        profile_form = self.profile_form_class(post_data, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # messages.success(request, 'Your profile was successfully updated!')
            return redirect('profile', slug=request.user.username)
        else:
            # messages.error(request, 'Please correct the error below.')
            return self.form_invalid()


class RegisterView(CreateView):
    template_name = "registration/register.html"
    form_class = RegisterForm

    def form_valid(self, form):
        to_return = super().form_valid(form)
        user = authenticate(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password1"],
        )
        login(self.request, user)
        return to_return

    def get_success_url(self):
        return reverse('home')


class Login(LoginView):
    # security issues (may not be a problem rn)/redirect issues with this (don't have permissions on this site)
    # for more info:
    # https://docs.djangoproject.com/en/3.0/topics/auth/default/#django.contrib.auth.views.LoginView
    redirect_authenticated_user = True

