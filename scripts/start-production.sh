#!/bin/bash

# Production Gunicorn startup script
# Usage: ./scripts/start-production.sh

set -e

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
fi

# Calculate optimal number of workers (2 * CPU cores + 1)
WORKERS=${WORKERS:-$(python -c "import multiprocessing; print(2 * multiprocessing.cpu_count() + 1)")}

echo "Starting Gunicorn with $WORKERS workers..."

exec gunicorn \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers $WORKERS \
    --worker-class ${WORKER_CLASS:-sync} \
    --timeout ${TIMEOUT:-30} \
    --keepalive ${KEEPALIVE:-2} \
    --max-requests ${MAX_REQUESTS:-1000} \
    --max-requests-jitter ${MAX_REQUESTS_JITTER:-100} \
    --preload \
    --user ${USER:-flaskuser} \
    --group ${GROUP:-flaskuser} \
    --log-level ${LOG_LEVEL:-info} \
    --access-logfile ${ACCESS_LOG:-/app/logs/access.log} \
    --error-logfile ${ERROR_LOG:-/app/logs/error.log} \
    --capture-output \
    --enable-stdio-inheritance \
    --pid ${PID_FILE:-/tmp/gunicorn.pid} \
    --daemon \
    "app:create_app()"
