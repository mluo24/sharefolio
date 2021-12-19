from django.contrib.auth.models import User
from django.shortcuts import reverse, get_object_or_404
from django.urls import reverse_lazy
# from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, RedirectView
from hitcount.views import HitCountDetailView
from friendship.models import Follow, Block
from rest_framework.decorators import action, renderer_classes
from stories.models import Category, Story, Chapter
# from django.contrib.auth.decorators import login_required
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from stories.serializers import CategorySerializer, ChapterSerializer, StorySerializer


# API STARTS HERE

class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

    def create(self, request):
        pass

    @action(detail=True, methods=['get', 'post'])
    @renderer_classes([JSONRenderer])
    def chapters(self, request, pk):
        story = self.get_object()
        chapters = story.chapter_set

        if request.method == 'GET':
            serializer = ChapterSerializer(chapters, many=True, context={'request': request})
            return Response(serializer.data)
        else:
            serializer = ChapterSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True)
    def published_chapters(self, request, pk):
        story = self.get_object()
        chapters = story.get_chapters()
        serializer = ChapterSerializer(chapters, many=True, context={'request': request})
        return Response(serializer.data)


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'


# NON API STARTS HERE

class StoriesView(ListView):
    model = Story
    template_name = 'stories/index.html'
    context_object_name = 'stories'
    paginate_by = 20


class StoryDetail(DetailView):
    model = Story
    context_object_name = 'story'
    query_pk_and_slug = True


class ChapterDetail(HitCountDetailView):
    model = Chapter
    context_object_name = 'chapter'
    pk_url_kwarg = 'chapter'
    count_hit = True

    def get_object(self):
        self.story = get_object_or_404(Story, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        return get_object_or_404(Chapter, pk=self.kwargs['chapter'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = self.story
        return context


class ChapterLikeToggle(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        temp_story = get_object_or_404(Story, id=self.kwargs['pk'], slug=self.kwargs['slug'])
        obj = get_object_or_404(Chapter, pk=self.kwargs['chapter'])
        url_ = obj.get_absolute_url()
        user = self.request.user
        if user.is_authenticated:
            if user in obj.likes.all():
                obj.likes.remove(user)
            else:
                obj.likes.add(user)
        return url_


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
    fields = ['title', 'description', 'cover', 'status', 'category', 'tags']

    def form_valid(self, form):
        story = form.save(commit=False)
        # self.object.parent_story = Story.objects.get(pk=form.cleaned_data['parent_story'])
        story.author = self.request.user
        story.save()
        form.save_m2m()  # for tags
        chapter = Chapter(parent_story=story)  # create new chapter
        chapter.save()
        self.success_url = reverse('chapter.update', kwargs={'pk': story.pk, 'chapter': chapter.pk})
        print(self.success_url)
        return super().form_valid(form)


class StoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Story
    template_name = "stories/update_story.html"
    fields = ['title', 'description', 'cover', 'status', 'category', 'tags']


class StoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Story
    # template_name = ""
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
        chapter = self.object
        chapter.parent_story = Story.objects.get(pk=self.request.POST.get('parent_story'))
        chapter.save()
        return HttpResponseRedirect(self.get_success_url())


class ChapterUpdateView(LoginRequiredMixin, UpdateView):
    model = Chapter
    pk_url_kwarg = 'chapter'
    template_name = "stories/update_chapter.html"
    fields = ['title', 'description', 'body', 'status']

    def get_success_url(self):
        print(self.object)
        return reverse('chapter',
                       kwargs={'pk': self.object.parent_story_id,
                               'slug': self.object.parent_story.slug,
                               'chapter': self.object.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['story'] = get_object_or_404(Story, id=self.kwargs['pk'])
        return context
    # template_name_suffix = '_update_form'


class ChapterDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Chapter
    # template_name = ""
    success_url = reverse_lazy('mystories')
    success_message = "Successfully deleted chapter"
