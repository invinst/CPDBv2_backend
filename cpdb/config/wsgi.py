"""
WSGI config for cpdb project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/howto/deployment/wsgi/
"""

import os
import newrelic.agent

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cpdb.settings")

newrelic.agent.initialize(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'newrelic.ini'))

application = get_wsgi_application()
application = newrelic.agent.wsgi_application()(application)
