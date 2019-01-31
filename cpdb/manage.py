#!/usr/bin/env python
import os
import sys

from django.core.management import execute_from_command_line

from mock import patch

if __name__ == '__main__':
    if 'test' in sys.argv:
        with patch('tqdm.tqdm', lambda iterable, *args, **kwargs: iterable):
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.test_without_migrations')
            os.environ.update({
                'AWS_ACCESS_KEY_ID': '',
                'AWS_SECRET_ACCESS_KEY': '',
                'AWS_DEFAULT_REGION': 'us-east-2',
            })
            execute_from_command_line(sys.argv)

    else:  # pragma: no cover
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
        execute_from_command_line(sys.argv)
