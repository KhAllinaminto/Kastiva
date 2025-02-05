# Gunicorn configuration file
import os

# Server socket
bind = f"0.0.0.0:{int(os.environ.get('PORT', 5000))}"
workers = 4
worker_class = 'sync'

# Logging
accesslog = '-'
errorlog = '-'
loglevel = 'info'

# Restart workers after this many requests
max_requests = 1000
max_requests_jitter = 50

# Process naming
proc_name = 'youtube-downloader'

# SSL config
keyfile = None
certfile = None

# Development settings
reload = False
