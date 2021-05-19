# For more settings, see: https://docs.gunicorn.org/en/stable/settings.html

workers = 1
worker_connections = 100
bind = "127.0.0.1:8008"
timeout = 30
