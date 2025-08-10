"""
WSGI config for Kermartin 3.0 project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kermartin_project.settings')

application = get_wsgi_application()
