from datetime import date
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.db.models.query import QuerySet

from apps.blog.queries import QUERIES

class Command(BaseCommand):
    help = 'Запуск и тестирование ORM запросов'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=int, help='Запустить только один конкретный запрос')
        parser.add_argument('--sql', action='store_true', help='Показать SQL-код')

    def handle(self, *args, **options):
        number = options.get('number')
        show_sql = options.get('sql')

        from apps.blog.models import Category
        
        cats = list(Category.objects.all()[:2])
        real_source = cats[0].slug if len(cats) > 0 else 'a'
        real_target = cats[1].slug if len(cats) > 1 else 'b'

        arguments = {
            4: {'slug': 'test-slug'},
            7: {'page': 2},
            8: {'word': 'a'},
            9: {'domain': 'example.com'}, 
            11: {'slugs': ['kino', 'sport']},
            12: {'year': 2026, 'month': 11},
            13: {'days': 30},
            14: {'start': date(2026, 1, 1), 'end': date(2026, 12, 31)},
            15: {'email': 'bekarys@django.com'}, 
            16: {'tag_slug': 'django'},
            17: {'category_slug': 'kino'},
            21: {'first_slug': 'django', 'second_slug': 'python'},
            22: {'text': 'a'}, 
            34: {'min_posts': 5},
            37: {'text': 'a'},
            40: {'name': 'Django ORM'},
            41: {'days': 5},
            42: {'category_slug': 'kino', 'tag_slug': 'django'},
            43: {'source_slug': real_source, 'target_slug': real_target},
            44: {},
        }

        if number:
            if number not in QUERIES:
                raise CommandError(f"Запрос под номером {number} не существует!")
            queries_to_run = [number]
        else:
            queries_to_run = [n for n in QUERIES.keys() if n not in range(40, 45)]

        for q_num in queries_to_run:
            func = QUERIES[q_num]
            kwargs = arguments.get(q_num, {})

            with CaptureQueriesContext(connection) as context:
                result = func(**kwargs)
                
                if isinstance(result, QuerySet):
                    items = list(result)
                    count = len(items)
                elif isinstance(result, list):
                    items = result
                    count = len(items)
                else:
                    items = [result]
                    count = 1 if result is not None else 0

            num_sql = len(context.captured_queries)
            
            self.stdout.write(self.style.SUCCESS(f"\n#{q_num} {func.__name__} — {num_sql} SQL query"))

            if show_sql and num_sql > 0:
                self.stdout.write(self.style.WARNING(context.captured_queries[0]["sql"]))

            if isinstance(result, (QuerySet, list)):
                for row in items[:5]:
                    ann_dict = {}
                    if isinstance(result, QuerySet) and result.query.annotations:
                        for ann in result.query.annotations.keys():
                            ann_dict[ann] = getattr(row, ann, None)
                    
                    if ann_dict:
                        self.stdout.write(f"  {row} {ann_dict}")
                    else:
                        self.stdout.write(f"  {row}")
                        
                self.stdout.write(self.style.NOTICE(f"  ({count} rows)"))
            else:
                self.stdout.write(f"  {result}")