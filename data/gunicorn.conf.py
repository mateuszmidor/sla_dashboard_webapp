# For more settings, see: https://docs.gunicorn.org/en/stable/settings.html

import multiprocessing

workers = 1
worker_connections = 100
bind = ":8050"
timeout = 30
worker_class = "gthread"
threads = 2 * multiprocessing.cpu_count() + 1  # this formula is suggested in gunicorn docs
