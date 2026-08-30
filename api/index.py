import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pitchpanel.settings")

import django  # noqa: E402

django.setup()

from django.core.wsgi import get_wsgi_application  # noqa: E402
from whitenoise import WhiteNoise  # noqa: E402

app = get_wsgi_application()
# Serve /static/* straight from the source static/ folder — no collectstatic
# step needed, which keeps the Vercel deploy simple.
app = WhiteNoise(app, root=str(BASE_DIR / "static"), prefix="static/")
