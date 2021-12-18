from django.contrib.auth.models import User
from hitcount.models import HitCountMixin
from rest_framework import serializers
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from stories.models import Story, Chapter, Category


class UserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ['id', 'url', 'first_name', 'last_name', 'username', 'email']


class AuthorListingField(serializers.RelatedField):
    def to_representation(self, value):
        return {
            "id": value.id,
            "username": value.username,
        }


class StorySerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    tags = TagListSerializerField()
    id = serializers.ReadOnlyField()
    author = AuthorListingField(read_only = True)

    word_count = serializers.SerializerMethodField()
    def get_word_count(self, obj):
        return obj.get_word_count()

    total_views = serializers.SerializerMethodField()
    def get_total_views(self, obj):
        return obj.get_total_views()

    total_likes = serializers.SerializerMethodField()
    def get_total_likes(self, obj):
        return obj.get_total_likes()

    class Meta:
        model = Story
        fields = ['id', 'url', 'title', 'slug', 'description', 'author', 'status', 'category', 'tags', 'word_count', 'total_views', 'total_likes', 'created_at', 'updated_at']


class ChapterSerializer(HitCountMixin, serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()
    # parent_story = serializers.PrimaryKeyRelatedField(read_only=True)

    hit_count = serializers.SerializerMethodField()
    def get_hit_count(self, obj):
        return obj.get_hit_count()

    class Meta:
        model = Chapter
        fields = ['id', 'url', 'parent_story', 'title', 'description', 'body', 'status', 'likes', 'hit_count', 'created_at']


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.ReadOnlyField()

    story_set = StorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'url', 'name', 'slug', 'description', 'story_set']