import datetime

from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse
from taggit.managers import TaggableManager


class Category(models.Model):
    # fields
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    description = models.CharField(max_length=255)

    # gets the stories that belong to this category
    def get_stories(self):
        list_of_pks = []
        story_set = self.story_set.all()
        for story in story_set:
            chapters = Chapter.objects.filter(parent_story=story)
            for chapter in chapters:
                is_valid = False
                if chapter.status != "draft":
                    is_valid = True
                if not is_valid:
                    list_of_pks.append(story.pk)
        return self.story_set.exclude(pk__in=list_of_pks)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "categories"

    def get_absolute_url(self):
        return reverse('categories.detail', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(Category, self).save(*args, **kwargs)


class Story(models.Model):
    # fields
    STATUS_LIST = (
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=9, choices=STATUS_LIST, default='ongoing')
    # add image field here
    # add num likes here
    # add bookmarks here
    # add views here
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)
    tags = TaggableManager()
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(default=timezone.now)

    def get_chapters_including_draft(self):
        return self.chapter_set.all()

    # gets the set of public chapters in this story
    def get_chapters(self):
        return self.chapter_set.filter(status="public")

    # gets the set of drafts
    def get_drafts(self):
        pass

    def get_num_chapters_including_draft(self):
        return self.get_chapters_including_draft().count()

    # gets the number of public chapters in this story
    def get_num_chapters(self):
        return self.get_chapters().count()

    def get_word_count(self):
        words = 0
        for chapter in self.get_chapters():
            current_text = strip_tags(chapter.body)
            words += len(current_text.split())
        return words

    def is_valid_story(self):
        return self.get_num_chapters() > 0

    def get_total_likes(self):
        total_likes = 0
        for chapter in self.chapter_set.all():
            total_likes += chapter.likes
        return total_likes

    def get_absolute_url(self):
        return reverse('story', args=[str(self.id), str(self.slug)])

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-updated_at"]
        get_latest_by = "-updated_at"
        verbose_name_plural = "stories"

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(Story, self).save(*args, **kwargs)


class Chapter(models.Model):
    STATUS_LIST = (
        ('draft', 'Draft'),
        ('public', 'Public'),
    )
    # make these optional if status is draft
    parent_story = models.ForeignKey(Story, on_delete=models.CASCADE)
    order = models.IntegerField(blank=True)
    title = models.CharField(max_length=255, null=True, blank=False)
    description = models.TextField(null=True, blank=False)
    body = RichTextField(config_name='normal', null=True, blank=False)
    status = models.CharField(max_length=6, choices=STATUS_LIST, default='draft')
    likes = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now=True)

    # def get_word_count(self):
    #     return 0

    def __str__(self):
        if self.title:
            return self.title
        else:
            return "null chapter"

    def get_absolute_url(self):
        return reverse('chapter', args=[str(self.parent_story.id), str(self.parent_story.slug), str(self.id)])

    def get_num_characters(self):
        # figure out how to return num characters in body field
        pass

    def save(self, *args, **kwargs):
        if not self.id:
            latest_chapter = Chapter.objects.filter(parent_story__chapter__parent_story=self.parent_story).order_by("-order").first()
            if latest_chapter is None:
                self.order = 1
            else:
                self.order = latest_chapter.order + 1
            self.parent_story.updated_at = timezone.now()
            self.parent_story.save()
        super(Chapter, self).save(*args, **kwargs)

    class Meta:
        ordering = ["order"]
        get_latest_by = "-order"

