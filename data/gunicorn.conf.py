# For more settings, see: https://docs.gunicorn.org/en/stable/settings.html

workers = 1
worker_connections = 100
bind = ":8050"
timeout = 30
