from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.db import transaction
from django.shortcuts import render, reverse, get_object_or_404, redirect
from django.views.generic import DetailView, CreateView, TemplateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, status
from rest_framework.decorators import action, renderer_classes
from rest_framework_extensions.mixins import NestedViewSetMixin

from base.forms import RegisterForm, PlainUserForm, UserProfileForm
from base.models import UserProfile
from base.serializers import LoginSerializer, RegisterSerializer, UserProfileSerializer, UserSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# API VIEW STARTS HERE
class UserViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    http_method_names = ['get', 'put']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        # if self.request.user.is_superuser:
        return User.objects.all()

    def get_object(self):
        lookup_field_value = self.kwargs[self.lookup_field]

        obj = User.objects.get(pk=lookup_field_value)
        self.check_object_permissions(self.request, obj)

        return obj


class UserProfileViewSet(NestedViewSetMixin, viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer


class LoginViewSet(viewsets.ModelViewSet, TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class RegistrationViewSet(viewsets.ModelViewSet, TokenObtainPairView):
    serializer_class = RegisterSerializer
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        res = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

        return Response({
            "user": serializer.data,
            "refresh": res["refresh"],
            "token": res["access"]
        }, status=status.HTTP_201_CREATED)


class RefreshViewSet(viewsets.ViewSet, TokenRefreshView):
    permission_classes = (AllowAny,)
    http_method_names = ['post']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


# PREVIOUS ROUTES START HERE

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

