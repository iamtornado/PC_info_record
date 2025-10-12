"""
WSGI config for pc_info_record project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pc_info_record.settings')

application = get_wsgi_application()
