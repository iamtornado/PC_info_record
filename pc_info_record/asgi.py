"""
ASGI config for pc_info_record project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pc_info_record.settings')

application = get_asgi_application()
