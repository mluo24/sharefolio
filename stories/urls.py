from django.urls import path
from . import views

urlpatterns = [
    path('stories/', views.StoriesView.as_view(), name="index"),
    path('stories/<int:pk>/<slug:slug>', views.StoryDetail.as_view(), name="story"),
    path('stories/<int:pk>/<slug:slug>/c/<int:chapter>', views.ChapterDetail.as_view(), name="chapter"),
    path('mystories/', views.MyStoryView.as_view(), name="mystories"),
    path('mystories/new', views.StoryCreateView.as_view(), name="story.new"),
    path('mystories/<int:pk>/edit', views.StoryUpdateView.as_view(), name="story.edit"),
    path('mystories/<int:pk>/delete', views.StoryDeleteView.as_view(), name="story.delete"),
    path('mystories/<int:pk>/newchapter', views.ChapterCreateView.as_view(), name="chapter.new"),
    path('mystories/<int:pk>/newchapter/<int:chapter>', views.ChapterUpdateView.as_view(), name="chapter.update"),
    path('categories/', views.CategoriesView.as_view(), name="categories"),
    path('categories/<slug:slug>', views.CategoryDetailView.as_view(), name="categories.detail"),
]
