# from django.shortcuts import render
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
# from django.contrib.sessions.models import Session
# from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from stories.models import Category, Story, Chapter
# from .forms import CreateStoryForm, CreateChapterForm

# from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin


class StoriesView(ListView):
    model = Story
    template_name = 'stories/index.html'
    context_object_name = 'stories'


class StoryDetail(DetailView):
    model = Story
    context_object_name = 'story'
    query_pk_and_slug = True


class ChapterDetail(DetailView):
    model = Chapter
    context_object_name = 'chapter'
    pk_url_kwarg = 'chapter'

    def get_object(self):
        self.story = get_object_or_404(Story, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return get_object_or_404(Chapter, pk=self.kwargs['chapter'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = self.story
        return context


class MyStoryView(LoginRequiredMixin, ListView):
    model = Story
    context_object_name = 'stories'
    template_name = 'stories/mystories.html'
    login_url = '/login/'

    def get_queryset(self):
        return Story.objects.filter(author=self.request.user)


class CategoriesView(ListView):
    model = Category
    template_name = 'stories/categories.html'
    context_object_name = 'categories'


class CategoryDetailView(DetailView):
    model = Category
    context_object_name = 'category'


class StoryCreateView(LoginRequiredMixin, CreateView):
    model = Story
    template_name = "stories/create_story.html"
    fields = ['title', 'description', 'status', 'category', 'tags']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        # self.object.parent_story = Story.objects.get(pk=form.cleaned_data['parent_story'])
        self.object.author = self.request.user
        self.object.save()
        self.chapter = Chapter(parent_story=self.object) # create new chapter
        self.chapter.save()
        self.success_url = reverse('chapter.update', kwargs={'pk': self.object.pk, 'chapter': self.chapter.pk})
        return HttpResponseRedirect(self.get_success_url())


class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Story
    template_name = "stories/update_story.html"
    fields = ['title', 'description', 'status', 'category', 'tags']


class StoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Story
    template_name = ""
    success_url = reverse_lazy('mystories')
    success_message = "Successfully deleted story"


class ChapterCreateView(LoginRequiredMixin, CreateView):
    model = Chapter
    template_name = "stories/create_chapter.html"
    fields = ['title', 'description', 'body', 'status']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = get_object_or_404(Story, id=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.parent_story = Story.objects.get(pk=self.request.POST.get('parent_story'))
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ChapterUpdateView(LoginRequiredMixin, UpdateView):
    model = Chapter
    pk_url_kwarg = 'chapter'
    template_name = "stories/update_chapter.html"
    fields = ['title', 'description', 'body', 'status']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = get_object_or_404(Story, id=self.kwargs['pk'])
        return context
    # template_name_suffix = '_update_form'


class ChapterDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Chapter
    template_name = ""
    success_url = reverse_lazy('mystories')
    success_message = "Successfully deleted chapter"
