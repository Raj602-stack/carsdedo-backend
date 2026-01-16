#!/bin/bash
# Deployment script for CarsDedo backend
# Usage: ./deploy.sh [production|staging]

set -e

ENVIRONMENT=${1:-production}

echo "🚀 Deploying CarsDedo backend ($ENVIRONMENT)..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please copy .env.example to .env and configure it."
    exit 1
fi

# Load environment variables
export $(grep -v '^#' .env | xargs)

# Validate required variables
if [ -z "$DJANGO_SECRET_KEY" ] || [ "$DJANGO_SECRET_KEY" = "your-secret-key-here-change-in-production" ]; then
    echo "❌ Error: DJANGO_SECRET_KEY not set or using default value!"
    exit 1
fi

if [ "$DJANGO_DEBUG" = "1" ] && [ "$ENVIRONMENT" = "production" ]; then
    echo "⚠️  Warning: DJANGO_DEBUG is set to 1 in production!"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Pull latest code (if using git)
if [ -d .git ]; then
    echo "📥 Pulling latest code..."
    git pull origin main || git pull origin master
fi

# Build and start containers
if [ "$ENVIRONMENT" = "production" ]; then
    echo "🏗️  Building production containers..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml build
    
    echo "🔄 Running migrations..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm web python backend/manage.py migrate --noinput
    
    echo "📦 Collecting static files..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml run --rm web python backend/manage.py collectstatic --noinput
    
    echo "🚀 Starting services..."
    docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    echo "🧹 Cleaning up old images..."
    docker image prune -f
else
    echo "🏗️  Building development containers..."
    docker compose build
    
    echo "🚀 Starting services..."
    docker compose up -d
fi

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if web service is running
if docker compose ps | grep -q "web.*Up"; then
    echo "✅ Deployment successful!"
    echo "📊 Service status:"
    docker compose ps
    echo ""
    echo "📝 View logs with: docker compose logs -f web"
else
    echo "❌ Deployment failed! Check logs:"
    docker compose logs web
    exit 1
fi
