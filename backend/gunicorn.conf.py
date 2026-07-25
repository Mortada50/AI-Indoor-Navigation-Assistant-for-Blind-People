# gunicorn.conf.py
# Gunicorn automatically reads this file when present in the working directory.
# This ensures our settings are applied regardless of how Render invokes gunicorn.

# Worker settings — 1 worker to prevent OOM on free-tier (512 MB RAM)
workers = 1
threads = 1
worker_class = "sync"

# Timeout — YOLO inference on CPU can take 30-90 seconds
# Default is 30s which causes WORKER TIMEOUT errors
timeout = 120

# Keep-alive
keepalive = 5

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Memory Leak Prevention
# Automatically restart the worker after 10 requests to completely flush RAM
max_requests = 10
max_requests_jitter = 2
