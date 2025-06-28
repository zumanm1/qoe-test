#!/bin/bash

# Deployment script for QoE Tool
# Usage: ./scripts/deploy.sh [environment] [action]
# Example: ./scripts/deploy.sh production deploy
# Example: ./scripts/deploy.sh production scale 5

set -e

ENVIRONMENT=${1:-development}
ACTION=${2:-deploy}
SCALE_COUNT=${3:-3}

echo "=== QoE Tool Deployment Script ==="
echo "Environment: $ENVIRONMENT"
echo "Action: $ACTION"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    print_error "Invalid environment. Use: development, staging, or production"
    exit 1
fi

# Load environment variables
ENV_FILE=".env.$ENVIRONMENT"
if [ -f "$ENV_FILE" ]; then
    print_status "Loading environment variables from $ENV_FILE"
    export $(cat "$ENV_FILE" | xargs)
else
    print_warning "Environment file $ENV_FILE not found. Using defaults."
fi

# Function to deploy application
deploy() {
    print_status "Starting deployment for $ENVIRONMENT environment..."
    
    # Build and start services
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml build --no-cache
        docker-compose -f docker-compose.prod.yml up -d
    else
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
    fi
    
    # Wait for services to be healthy
    print_status "Waiting for services to be healthy..."
    sleep 30
    
    # Run database migrations
    print_status "Running database migrations..."
    docker-compose exec web flask db upgrade
    
    # Check health
    print_status "Checking application health..."
    curl -f http://localhost:5000/health || {
        print_error "Health check failed!"
        exit 1
    }
    
    print_status "Deployment completed successfully!"
}

# Function to scale application
scale() {
    print_status "Scaling web service to $SCALE_COUNT instances..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml up -d --scale web=$SCALE_COUNT
    else
        docker-compose up -d --scale web=$SCALE_COUNT
    fi
    
    print_status "Scaled to $SCALE_COUNT instances"
}

# Function to monitor deployment
monitor() {
    print_status "Monitoring application..."
    
    echo "=== Container Status ==="
    docker-compose ps
    
    echo -e "\n=== Resource Usage ==="
    docker stats --no-stream
    
    echo -e "\n=== Recent Logs ==="
    docker-compose logs --tail=50 web
}

# Function to rollback deployment
rollback() {
    print_status "Rolling back deployment..."
    
    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.prod.yml down
        # Here you would typically restore from a backup or previous image
        docker-compose -f docker-compose.prod.yml up -d
    else
        docker-compose down
        docker-compose up -d
    fi
    
    print_status "Rollback completed"
}

# Function to backup database
backup() {
    print_status "Creating database backup..."
    
    BACKUP_FILE="backups/qoe_tool_$(date +%Y%m%d_%H%M%S).sql"
    mkdir -p backups
    
    docker-compose exec -T db pg_dump -U qoe_user qoe_tool > "$BACKUP_FILE"
    
    print_status "Database backup created: $BACKUP_FILE"
}

# Execute action
case $ACTION in
    deploy)
        deploy
        ;;
    scale)
        scale
        ;;
    monitor)
        monitor
        ;;
    rollback)
        rollback
        ;;
    backup)
        backup
        ;;
    *)
        print_error "Invalid action. Use: deploy, scale, monitor, rollback, or backup"
        exit 1
        ;;
esac

print_status "Script completed successfully!"
