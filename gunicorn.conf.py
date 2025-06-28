"""
Gunicorn configuration file for Flask application
Usage: gunicorn --config gunicorn.conf.py "app:create_app()"
"""

import multiprocessing
import os

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = os.getenv('WORKER_CLASS', 'sync')
worker_connections = 1000
timeout = int(os.getenv('TIMEOUT', 30))
keepalive = int(os.getenv('KEEPALIVE', 2))

# Restart workers after this many requests to prevent memory leaks
max_requests = int(os.getenv('MAX_REQUESTS', 1000))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', 100))

# Load application before forking workers
preload_app = True

# Security
user = os.getenv('USER', 'flaskuser')
group = os.getenv('GROUP', 'flaskuser')

# Logging
loglevel = os.getenv('LOG_LEVEL', 'info')
accesslog = os.getenv('ACCESS_LOG', '-')  # stdout
errorlog = os.getenv('ERROR_LOG', '-')   # stderr
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'qoe-tool-flask'

# PID file
pidfile = os.getenv('PID_FILE', '/tmp/gunicorn.pid')

# Server mechanics
daemon = os.getenv('DAEMON', 'false').lower() == 'true'
tmp_upload_dir = None

# SSL (if using HTTPS)
keyfile = os.getenv('SSL_KEYFILE')
certfile = os.getenv('SSL_CERTFILE')

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("Server is ready. Spawning workers")

def worker_int(worker):
    """Called just after a worker has been killed by SIGINT."""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("worker received SIGABRT signal")
