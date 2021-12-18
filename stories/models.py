from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.utils import timezone
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse
from hitcount.models import HitCount, HitCountMixin
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
            if story.get_chapters().count() == 0:
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
    slug = models.SlugField( blank=True)
    description = models.TextField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=9, choices=STATUS_LIST, default='ongoing')
    # add image field here
    cover = models.ImageField(upload_to='user_uploads/covers', default='noimage.png')
    bookmarks = models.ManyToManyField(User, blank=True, related_name="story_bookmarks", verbose_name='bookmarks')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=False)
    tags = TaggableManager()
    # distinguish publish vs created
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)

    def get_chapters_including_draft(self):
        return self.chapter_set.all()

    # gets the set of public chapters in this story
    def get_chapters(self):
        return self.chapter_set.filter(status="public")

    # gets the set of drafts
    def get_drafts(self):
        return self.chapter_set.filter(status="draft")

    def get_num_chapters_including_draft(self):
        return self.get_chapters_including_draft().count()

    # gets the number of public chapters in this story
    def get_num_chapters(self):
        return self.get_chapters().count()

    def get_word_count(self):
        words = 0
        for chapter in self.get_chapters():
            words += chapter.get_words()
        return words

    def get_total_views(self):
        total_views = 0
        for chapter in self.get_chapters():
            total_views += chapter.hit_count.hits
        return total_views

    def is_valid_story(self):
        return self.get_num_chapters() > 0

    def get_total_likes(self):
        total_likes = 0
        for chapter in self.chapter_set.all():
            if chapter.likes is not None or chapter.likes != "":
                total_likes += chapter.likes.count()
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
        if not self.pk:
            self.created_at = timezone.now()
        self.slug = slugify(self.title)
        super(Story, self).save(*args, **kwargs)


class Chapter(models.Model, HitCountMixin):
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
    likes = models.ManyToManyField(User, blank=True, related_name="chapter_likes", verbose_name='likes')
    hit_count_generic = GenericRelation(HitCount, object_id_field='object_pk',
                                        related_query_name='hit_count_generic_relation')
    # distinguish publish vs created
    created_at = models.DateTimeField()
    # published_at = models.DateTimeField()

    def __str__(self):
        if self.title:
            return self.title
        else:
            return "null chapter"

    def get_hit_count(self):
        return self.hit_count.hits

    def get_absolute_url(self):
        return reverse('chapter', kwargs={'pk': self.parent_story_id,
                                          'slug': self.parent_story.slug,
                                          'chapter': self.id})

    def get_words(self):
        return len(strip_tags(self.body).split())

    def get_like_url(self):
        return reverse('liketoggle', args=[str(self.parent_story.id), str(self.parent_story.slug), str(self.id)])

    def save(self, *args, **kwargs):
        if not self.id:
            self.created_at = timezone.now()
            latest_chapter = Chapter.objects.filter(parent_story__chapter__parent_story=self.parent_story).order_by("-order").first()
            if latest_chapter is None:
                self.order = 1
            else:
                self.order = latest_chapter.order + 1
        if self.status != "draft":
            self.parent_story.save()
        super(Chapter, self).save(*args, **kwargs)

    class Meta:
        ordering = ["order"]
        get_latest_by = "-order"

