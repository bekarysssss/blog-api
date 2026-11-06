from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Post, Comment, Category, Tag

@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}

@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {"slug": ("name",)}
    pass

@admin.register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'author', 'status', 'category')
    list_filter = ('status', 'category')
    search_fields = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ('tags',)

    fieldsets = (
        ("Основной контент", {
            "fields": ("title", "content", "author")
        }),
        ("Категория и Теги", {
            "fields": ("category", "tags")
        }),
        ("Дополнительно", {
            "fields": ("slug", "status"),
            "classes": ("collapse",)
        }),
    )

@admin.register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('post', 'author', 'get_short_text')
    list_filter = ('author',)

    @admin.display(description='Текст')
    def get_short_text(self, obj):
        if len(obj.text) > 50:
            return obj.text[:50] + "..."
        return obj.text