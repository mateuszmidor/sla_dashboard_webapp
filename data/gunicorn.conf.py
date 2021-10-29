# For more settings, see: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing

wsgi_app = "main:run()"
workers = 1  # only one worker process to maximize mesh results caching profits
bind = ":8050"
timeout = 30
# Worker is changed to prevent worker timeouts
# See: https://github.com/benoitc/gunicorn/issues/1801#issuecomment-585886471
worker_class = "gthread"
threads = 2 * multiprocessing.cpu_count() + 1  # this formula is suggested in gunicorn docs
