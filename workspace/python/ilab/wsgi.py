import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from flask_app import create_app

application = create_app()

# Gunicorn entrypoint: gunicorn wsgi:application
# Example: gunicorn -w 1 -b 0.0.0.0:8000 --timeout 120 wsgi:application
#
# NOTE: Use exactly 1 worker (-w 1). The in-memory job/quiz/result stores are
# process-local. Multiple workers will silently lose data across requests.
# For multi-worker production deployments, replace TTLStore with Redis.
