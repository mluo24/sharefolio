# Generated by Django 3.0.4 on 2021-08-13 04:15

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import hitcount.models
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0003_taggeditem_add_unique_index'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.CharField(max_length=255)),
            ],
            options={
                'verbose_name_plural': 'categories',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Story',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('slug', models.SlugField(blank=True, unique=True)),
                ('description', models.TextField()),
                ('status', models.CharField(choices=[('ongoing', 'Ongoing'), ('completed', 'Completed')], default='ongoing', max_length=9)),
                ('cover', models.ImageField(default='noimage.png', upload_to='user_uploads/covers')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('bookmarks', models.ManyToManyField(blank=True, related_name='story_bookmarks', to=settings.AUTH_USER_MODEL, verbose_name='bookmarks')),
                ('category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stories.Category')),
                ('tags', taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'verbose_name_plural': 'stories',
                'ordering': ['-updated_at'],
                'get_latest_by': '-updated_at',
            },
        ),
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.IntegerField(blank=True)),
                ('title', models.CharField(max_length=255, null=True)),
                ('description', models.TextField(null=True)),
                ('body', ckeditor.fields.RichTextField(null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('public', 'Public')], default='draft', max_length=6)),
                ('created_at', models.DateTimeField()),
                ('likes', models.ManyToManyField(blank=True, related_name='chapter_likes', to=settings.AUTH_USER_MODEL, verbose_name='likes')),
                ('parent_story', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stories.Story')),
            ],
            options={
                'ordering': ['order'],
                'get_latest_by': '-order',
            },
            bases=(models.Model, hitcount.models.HitCountMixin),
        ),
    ]
