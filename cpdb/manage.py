#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    if 'test' in sys.argv:
        default_settings_module = 'config.settings.test'
    else:
        default_settings_module = "config.settings.local"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", default_settings_module)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
