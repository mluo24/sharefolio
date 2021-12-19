"""sharefolio URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from rest_framework import routers
from stories import views as story_views
from base import views as base_views

router = routers.DefaultRouter()
router.register(r'stories', story_views.StoryViewSet)
router.register(r'chapters', story_views.ChapterViewSet)
router.register(r'categories', story_views.CategoryViewSet)

# base
router.register(r'users', base_views.UserViewSet)
router.register(r'auth/login', base_views.LoginViewSet, basename='auth-login')
router.register(r'auth/register', base_views.RegistrationViewSet, basename='auth-register')
router.register(r'auth/refresh', base_views.RefreshViewSet, basename='auth-refresh')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stories.urls')),
    path('', include('base.urls')),
    path('', include('django.contrib.auth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('comments/', include('django_comments.urls')),
    path('hitcount/', include(('hitcount.urls', 'hitcount'), namespace='hitcount')),
    path('friendship/', include('friendship.urls')),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

