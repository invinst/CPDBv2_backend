#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'test' in sys.argv:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test_without_migrations")
    else:
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")  # pragma: no cover

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
