from django.urls import path
from . import views

# accounts and main site and stuff
urlpatterns = [
    path('', views.home, name="home"),
    path('user/<slug:slug>', views.UserProfileView.as_view(), name="profile"),
    path('user/<slug:slug>/stories', views.UserProfileView.as_view(), name="profile.stories"),
    path('register/', views.RegisterView.as_view(), name="register"),
    path('login/', views.Login.as_view(), name="login"),
]

