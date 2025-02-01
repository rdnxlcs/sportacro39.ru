import os
import sys

try:
  sys.path.remove('/usr/lib/python3/dist-packages')
except:
  pass

sys.path.append('/home/c/centromebel/acro/public_html/ACRO/')
sys.path.append('/home/c/centromebel/acro/venv/lib/python3.10/site-packages/')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ACRO.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()