from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile


# class UserInline(admin.StackedInline):
#     list_display = ('username', 'email', 'first_name', 'last_name')
#     model = User


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio', 'location', 'birth_date')


admin.site.register(UserProfile, UserProfileAdmin)
