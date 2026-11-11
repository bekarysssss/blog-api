from django.db.models.functions import Coalesce, Concat, TruncMonth, Cast
from django.db.models import FloatField
from django.db.models import QuerySet, Q, F, Value, Count, Avg, Min, Max, Case, When, Subquery, OuterRef, Exists
from django.utils.text import slugify
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import QuerySet, Q, F, Value, Count, Avg, Min, Max, Case, When
from django.db.models.functions import Coalesce, Concat, TruncMonth
from django.db.models import QuerySet, Q, F, Value, Count, Avg, Min, Max
from django.db.models.functions import Coalesce
from django.db.models import Value
from django.db.models import Q, F
from datetime import timedelta
from datetime import date
from django.utils import timezone
from django.db.models import QuerySet
from apps.blog.models import Category, Post, Comment, Tag
from django.contrib.auth import get_user_model

User = get_user_model()

# 1 level
def categories_by_name() -> QuerySet[Category]:
    """1. All categories, sorted by name A → Z."""
    return Category.objects.all().order_by('name')

def published_posts() -> QuerySet[Post]:
    """2. Published posts, newest first."""
    return Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-created_at')

def newest_published_posts() -> QuerySet[Post]:
    """3. The 5 newest published posts."""
    return Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-created_at')[:5]

def post_by_slug(slug: str) -> Post | None:
    """4. The post with this slug, or None if there is no such post."""
    return Post.objects.filter(slug=slug).first()

def active_users_count() -> int:
    """5. Number of active users. Staff users are not counted."""
    return User.objects.filter(is_active=True, is_staff=False).count()

def has_drafts() -> bool:
    """6. True if there is at least one draft post."""
    return Post.objects.filter(status=Post.Status.DRAFT).exists()

def published_posts_page(page: int) -> QuerySet[Post]:
    """7. One page of published posts, newest first. 10 posts per game."""
    start = (page - 1) * 10
    end = start + 10
    return Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-created_at')[start:end]

# 2 level
def posts_with_word_in_title(word: str) -> QuerySet[Post]:
    """8. Posts whose title contains word. Letter case does not matter."""
    return Post.objects.filter(title__icontains=word)

def users_with_email_domain(domain: str) -> QuerySet[User]:
    """9. Users whose email ends with @ + domain."""
    return User.objects.filter(email__iendswith=f"@{domain}")

def posts_without_category() -> QuerySet[Post]:
    """10. Posts that have no category."""
    return Post.objects.filter(category__isnull=True)

def categories_by_slugs(slugs: list[str]) -> QuerySet[Category]:
    """11. Categories whose slug is in the list slugs."""
    return Category.objects.filter(slug__in=slugs)

def posts_in_month(year:int, month: int) -> QuerySet[Post]:
    """12. Posts created in this month of this year."""
    return Post.objects.filter(created_at__year=year, created_at__month=month)

def posts_last_days(days: int) -> QuerySet[Post]:
    """13. Posts created in the last days days."""
    from datetime import timedelta
    start_time = timezone.now() - timedelta(days=days)
    return Post.objects.filter(created_at__gte=start_time)

def posts_between(start: date, end: date) -> QuerySet[Post]:
    """14. Posts created from start to end. Both start and end days are included."""
    return Post.objects.filter(created_at__date__range=(start, end))

# 3 level
def author_published_posts(email: str) -> QuerySet[Post]:
    """15. Published posts of the author with this email."""
    return Post.objects.filter(status='published', author__email__iexact=email)

def posts_with_tag(tag_slug: str) -> QuerySet[Post]:
    """16. Posts that have the tag with this slug."""
    return Post.objects.filter(tags__slug=tag_slug)

def comments_in_category(category_slug: str) -> QuerySet[Comment]:
    """17. Comments on posts of the category with this slug."""
    return Comment.objects.filter(post__category__slug=category_slug)

def users_with_published_posts() -> QuerySet[User]:
    """18. Users who have at least one published post."""
    return User.objects.filter(posts__status='published').distinct()

def posts_without_tags() -> QuerySet[Post]:
    """19. Posts that have no tags."""
    return Post.objects.filter(tags__isnull=True)

def users_without_comments() -> QuerySet[User]:
    """20. Users who have never written a comment."""
    return User.objects.filter(comment__isnull=True)

def posts_with_both_tags(first_slug: str, second_slug: str) -> QuerySet[Post]:
    """21. Posts that have both tags."""
    return Post.objects.filter(tags__slug=first_slug).filter(tags__slug=second_slug)

# 4 level
def search_posts(text: str) -> QuerySet[Post]:
    """22. Posts that have text in the title or in the body."""
    return Post.objects.filter(Q(title__icontains=text) | Q(content__icontains=text))

def published_posts_missing_info() -> QuerySet[Post]:
    """23. Published posts that have no category or no tags."""
    return Post.objects.filter(
        Q(status='published') & (Q(category__isnull=True) | Q(tags__isnull=True))
    ).distinct()

def edited_posts() -> QuerySet[Post]:
    """24. Posts that were edited more than 1 hour after they were created."""
    return Post.objects.filter(updated_at__gt=F('created_at') + timedelta(hours=1))

def comments_by_post_author() -> QuerySet[Comment]:
    """25. Comments that the author of the post wrote under their own post."""
    return Comment.objects.filter(author=F('post__author'))

def comments_before_post() -> QuerySet[Comment]:
    """26. Comments created before their post."""
    return Comment.objects.filter(created_at__lt=F('post__created_at'))

# 5 level
def published_authors_emails() -> list[str]:
    """27. Emails of authors who have published posts. Unique, sorted A → Z. A plain list of strings."""
    return list(
        Post.objects.filter(status='published')
        .values_list('author__email', flat=True)
        .order_by('author__email')
        .distinct()
    )

def published_posts_overview() -> list[dict]:
    """28. One dict for each published post with keys: title, author_email, category_name."""
    return list(
        Post.objects.filter(status='published')
        .values(
            'title',
            author_email=F('author__email'), 
            category_name=Coalesce('category__name', Value('Uncategorized'))
        )
    )

# 6 level
def posts_stats() -> dict:
    """29. Stats: total, published, drafts, first_post_at, last_post_at in one query."""
    return Post.objects.aggregate(
        total=Count('id'),
        published=Count('id', filter=Q(status='published')),
        drafts=Count('id', filter=Q(status='draft')),
        first_post_at=Min('created_at'),
        last_post_at=Max('created_at')
    )

def average_comments_per_post() -> float:
    """30. Average comments on a published post, rounded to 2 digits."""
    result = Post.objects.filter(status='published').annotate(
        comment_count=Count('comments') 
    ).aggregate(
        avg_comments=Avg('comment_count')
    )
    
    avg_value = result.get('avg_comments')
    if avg_value is None:
        return 0.0
    return round(avg_value, 2)

# 7 level
def categories_with_post_count() -> QuerySet[Category]:
    """31. Every category with post_count. Most posts first. Same count → sort by name."""
    return Category.objects.annotate(
        post_count=Count('posts') 
    ).order_by('-post_count', 'name')

def categories_with_published_count() -> QuerySet[Category]:
    """32. Every category with published_count, including 0."""
    return Category.objects.annotate(
        published_count=Count('posts', filter=Q(posts__status='published')) 
    )

def top_authors() -> QuerySet[User]:
    """33. The top 5 users by number of published posts, with published_count."""
    return User.objects.annotate(
        published_count=Count('posts', filter=Q(posts__status='published'))
    ).order_by('-published_count')[:5]

def popular_tags(min_posts: int) -> QuerySet[Tag]:
    """34. Tags used in at least min_posts posts, with post_count."""
    return Tag.objects.annotate(
        post_count=Count('posts') 
    ).filter(post_count__gte=min_posts)

def posts_per_status() -> list[dict]:
    """35. The number of posts for each status."""
    return list(
        Post.objects.values('status').annotate(count=Count('id'))
    )

def users_activity() -> QuerySet[User]:
    """36. Every user with post_count and comment_count. Both numbers must be correct."""
    return User.objects.annotate(
        post_count=Count('posts', distinct=True),
        comment_count=Count('comment', distinct=True)
    )

# 8 level
def search_users_by_full_name(text: str) -> QuerySet[User]:
    """37. Users whose full name ("First Last") contains text."""
    return User.objects.annotate(
        full_name=Concat('first_name', Value(' '), 'last_name')
    ).filter(full_name__icontains=text)

def published_posts_per_month() -> list[dict]:
    """38. The number of published posts in each month, oldest first."""
    return list(
        Post.objects.filter(status='published')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('id'))
        .order_by('month')
    )

def posts_with_popularity() -> QuerySet[Post]:
    """39. Every post with comment_count and popularity ("hot", "normal", "quiet")."""
    return Post.objects.annotate(
        comment_count=Count('comments')
    ).annotate(
        popularity=Case(
            When(comment_count__gte=10, then=Value('hot')),
            When(comment_count__gte=3, then=Value('normal')),
            default=Value('quiet')
        )
    )

# 9 level
def get_or_create_tag(name: str) -> tuple[Tag, bool]:
    """40. Return the tag with this name. Create it if it does not exist."""
    slug = slugify(name, allow_unicode=True)
    return Tag.objects.get_or_create(slug=slug, defaults={'name': name})

def publish_old_drafts(days: int) -> int:
    """41. All drafts older than days become published. Return how many posts changed."""
    threshold = timezone.now() - timedelta(days=days)
    return Post.objects.filter(
        status='draft', 
        created_at__lt=threshold
    ).update(
        status='published', 
        updated_at=timezone.now()
    )

def tag_category_posts(category_slug: str, tag_slug: str) -> int:
    """42. Add the tag to every post of the category."""
    tag = Tag.objects.get(slug=tag_slug)
    posts = Post.objects.filter(category__slug=category_slug)
    count = posts.count()
    tag.posts.add(*posts) 
    return count

def merge_categories(source_slug: str, target_slug: str) -> int:
    """43. Move all posts to target category, then delete source category."""
    source_cat = Category.objects.get(slug=source_slug)
    target_cat = Category.objects.get(slug=target_slug)
    
    moved_count = Post.objects.filter(category=source_cat).update(category=target_cat)
    source_cat.delete()
    
    return moved_count

def delete_inactive_users_comments() -> int:
    """44. Delete all comments written by inactive users."""
    deleted_count, _ = Comment.objects.filter(author__is_active=False).delete()
    return deleted_count

# 10 level
def posts_with_authors_and_categories() -> QuerySet[Post]:
    """45. All published posts with their author and category (to avoid N+1)."""
    return Post.objects.select_related('author', 'category').filter(status='published')

def posts_with_tags() -> QuerySet[Post]:
    """46. All published posts with their tags (to avoid N+1)."""
    return Post.objects.prefetch_related('tags').filter(status='published')

def categories_with_posts() -> QuerySet[Category]:
    """47. All categories with their posts (to avoid N+1)."""
    return Category.objects.prefetch_related('posts')

# 11 level
def posts_with_latest_comment_author() -> QuerySet[Post]:
    """48. Every post with the email of the author of its latest comment (using Subquery)."""
    latest_comment_email = Comment.objects.filter(
        post=OuterRef('pk')
    ).order_by('-created_at').values('author__email')[:1]

    return Post.objects.annotate(
        latest_comment_author_email=Subquery(latest_comment_email)
    )

def authors_with_recent_post() -> QuerySet[User]:
    """49. Users who have at least one published post created in the last 30 days (using Exists)."""
    from datetime import timedelta
    threshold = timezone.now() - timedelta(days=30)
    
    recent_posts = Post.objects.filter(
        author=OuterRef('pk'),
        status='published',
        created_at__gte=threshold
    )
    return User.objects.filter(Exists(recent_posts))

from django.db.models.functions import Cast

from django.db.models import ExpressionWrapper, FloatField

def posts_newer_than_category_avg() -> QuerySet[Post]:
    """50. Posts created more recently than the average post creation date of their category (using Subquery)."""
    category_avg_date = Post.objects.filter(
        category=OuterRef('category_id')
    ).values('category').annotate(
        avg_date=Avg(Cast('created_at', FloatField()))
    ).values('avg_date')
    return Post.objects.annotate(
        cat_avg_date=Subquery(category_avg_date),
        created_float=Cast('created_at', FloatField())
    ).filter(
        created_float__gt=F('cat_avg_date')
    )

QUERIES = {
    1: categories_by_name,
    2: published_posts,
    3: newest_published_posts,
    4: post_by_slug,
    5: active_users_count,
    6: has_drafts,
    7: published_posts_page,
    8: posts_with_word_in_title,
    9: users_with_email_domain,
    10: posts_without_category,
    11: categories_by_slugs,
    12: posts_in_month,
    13: posts_last_days,
    14: posts_between,
    15: author_published_posts,
    16: posts_with_tag,
    17: comments_in_category,
    18: users_with_published_posts,
    19: posts_without_tags,
    20: users_without_comments,
    21: posts_with_both_tags,
    22: search_posts,
    23: published_posts_missing_info,
    24: edited_posts,
    25: comments_by_post_author,
    26: comments_before_post,
    27: published_authors_emails,
    28: published_posts_overview,
    29: posts_stats,
    30: average_comments_per_post,
    31: categories_with_post_count,
    32: categories_with_published_count,
    33: top_authors,
    34: popular_tags,
    35: posts_per_status,
    36: users_activity,
    37: search_users_by_full_name,
    38: published_posts_per_month,
    39: posts_with_popularity,
    40: get_or_create_tag,
    41: publish_old_drafts,
    42: tag_category_posts,
    43: merge_categories,
    44: delete_inactive_users_comments,
    45: posts_with_authors_and_categories,
    46: posts_with_tags,
    47: categories_with_posts,
    48: posts_with_latest_comment_author,
    49: authors_with_recent_post,
    50: posts_newer_than_category_avg,
}