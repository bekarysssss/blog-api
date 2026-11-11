import random
import time
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils.text import slugify
from django.utils import timezone
from faker import Faker

from apps.blog.models import Post, Comment, Category, Tag

User = get_user_model()

class Command(BaseCommand):
    help = 'Заполнение базы данных с реалистичными датами'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=20, help='Количество пользователей')
        parser.add_argument('--posts', type=int, default=100, help='Количество постов')
        parser.add_argument('--comments', type=int, default=500, help='Количество комментариев')
        parser.add_argument('--clear', action='store_true', help='Очистить старые данные перед созданием')

    def handle(self, *args, **options):
        users_count = options['users']
        posts_count = options['posts']
        comments_count = options['comments']
        clear = options['clear']

        if users_count < 0 or posts_count < 0 or comments_count < 0:
            raise CommandError("Количество не может быть отрицательным!")
        if users_count == 0 and (posts_count > 0 or comments_count > 0):
            raise CommandError("Нельзя создать посты и комментарии, если нет юзеров-авторов!")
        
        fake = Faker()
        start_time = time.time()
        now = timezone.now()

        if clear:
            self.stdout.write("Удаляем старые данные")
            Comment.objects.all().delete()
            Post.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("База очищена!"))

        self.stdout.write("Создаем пользователей...")
        users_to_create = []
        hashed_password = make_password("Password123!")

        for _ in range(users_count):
            user = User(
                email=fake.unique.email(),
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                password=hashed_password,
                is_active=random.choice([True, True, True, False]), 
                is_staff=random.choice([True, False, False, False]) 
            )
            users_to_create.append(user)

        User.objects.bulk_create(users_to_create)
        all_users = list(User.objects.all())

        self.stdout.write("Создаем категории и теги...")
        category_names = ['Технологии', 'Кино', 'Спорт', 'Путешествия', 'Еда', 'Искусство', 'Музыка', 'Наука']
        tag_names = ['django', 'python', 'новости', 'обзор', 'лайфхак', 'интересное', 'топ10', 'мнение']

        categories = Category.objects.bulk_create([Category(name=name, slug=slugify(name, allow_unicode=True)) for name in category_names])
        tags = Tag.objects.bulk_create([Tag(name=name, slug=slugify(name, allow_unicode=True)) for name in tag_names])

        self.stdout.write("Создаем посты...")
        posts_to_create = []
        for _ in range(posts_count):
            title = fake.sentence(nb_words=6)
            post = Post(
                title=title,
                slug=slugify(title) + f"-{random.randint(1000, 9999)}",
                content=fake.text(max_nb_chars=1000),
                status=random.choices(['published', 'draft'], weights=[70, 30])[0], 
                author=random.choice(all_users),
                category=random.choices([random.choice(categories), None], weights=[90, 10])[0]
            )
            posts_to_create.append(post)
        
        created_posts = Post.objects.bulk_create(posts_to_create)

        posts_to_update = []
        for post in created_posts:
            days_ago = random.randint(0, 365)
            post.created_at = now - timedelta(days=days_ago)
            
            if random.random() < 0.3:
                edit_delay = random.randint(1, 30)
                potential_updated_at = post.created_at + timedelta(days=edit_delay)
                post.updated_at = min(potential_updated_at, now)
            else:
                post.updated_at = post.created_at
                
            posts_to_update.append(post)
            
            post_tags = random.sample(list(tags), k=random.randint(1, 4))
            post.tags.set(post_tags)

        Post.objects.bulk_update(posts_to_update, ['created_at', 'updated_at'])

        self.stdout.write("Создаем комментарии...")
        published_posts = [p for p in created_posts if p.status == 'published']

        if published_posts and comments_count > 0:
            comments_to_create = []
            for _ in range(comments_count):
                parent_post = random.choice(published_posts)
                
                max_seconds_delay = int((now - parent_post.created_at).total_seconds())
                delay_seconds = random.randint(0, max_seconds_delay) if max_seconds_delay > 0 else 0
                
                comment_created_at = parent_post.created_at + timedelta(seconds=delay_seconds)
                
                comment = Comment(
                    post=parent_post,
                    author=random.choice(all_users),
                    text=" ".join(fake.sentences(nb=random.randint(1, 3)))
                )
                comment._temp_created_at = comment_created_at
                comments_to_create.append(comment)
                
            created_comments = Comment.objects.bulk_create(comments_to_create)
            
            for comment in created_comments:
                comment.created_at = comment._temp_created_at
                
            Comment.objects.bulk_update(created_comments, ['created_at'])

        end_time = time.time()
        self.stdout.write(self.style.SUCCESS(
            f"Успешно создано за {end_time - start_time:.2f} секунд:\n"
            f"- Пользователей: {users_count}\n"
            f"- Постов: {posts_count} (даты разбросаны)\n"
            f"- Комментариев: {comments_count} (даты привязаны к постам)\n"
            f"- Категорий: {len(categories)}\n"
            f"- Тегов: {len(tags)}"
        ))