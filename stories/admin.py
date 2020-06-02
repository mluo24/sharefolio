from django.contrib import admin
from .models import Category, Story, Chapter

# Register your models here.


class ChapterInline(admin.StackedInline):
    list_display = ('title', 'description', 'status', 'order', 'created_at')
    model = Chapter


class StoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'description', 'category', 'tag_list', 'status', 'created_at', 'updated_at')
    inlines = [ChapterInline]

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')

    def tag_list(self, obj):
        return u", ".join(o.name for o in obj.tags.all())


admin.site.register(Story, StoryAdmin)
admin.site.register(Category)

