import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_signals_orm_0x04.settings')
django.setup()