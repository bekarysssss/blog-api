import os
import sys
from pathlib import Path
from decouple import config


def main() -> None:
    current_path = Path(__file__).resolve().parent
    sys.path.append(str(current_path))

    env_id = config('BLOG_ENV_ID', default='local')

    if env_id == 'prod':
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.env.prod')
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.env.local')

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
