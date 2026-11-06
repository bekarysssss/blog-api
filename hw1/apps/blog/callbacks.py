from django.contrib.auth import get_user_model
from django.db.models import Count
from .models import Post, Comment

User = get_user_model()

def dashboard_callback(request, context):
    users_count = User.objects.count()
    posts_count = Post.objects.filter(status='published').count()
    drafts_count = Post.objects.filter(status='draft').count()
    comments_count = Comment.objects.count()
    
    top_authors = User.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]

    context.update({
        "users_count": users_count,
        "posts_count": posts_count,
        "drafts_count": drafts_count,
        "comments_count": comments_count,
        "top_authors": top_authors,
    })
    return context