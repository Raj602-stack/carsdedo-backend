#!/bin/bash
# VPS Deployment Script for CarsDedo Backend
# Usage: ./deploy-vps.sh

set -e

echo "🚀 CarsDedo Backend VPS Deployment"
echo "=================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env file with your production values before continuing."
    echo "   Important: Set DJANGO_SECRET_KEY, POSTGRES_PASSWORD, and ALLOWED_HOSTS"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

# Determine compose command
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo ""
echo "📦 Building and starting containers..."
$COMPOSE_CMD -f docker-compose.vps.yml up -d --build

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

echo ""
echo "🔍 Checking service status..."
$COMPOSE_CMD -f docker-compose.vps.yml ps

echo ""
echo "📋 Recent logs:"
$COMPOSE_CMD -f docker-compose.vps.yml logs --tail=20 backend

echo ""
echo "📊 Importing CSV data..."
sleep 3
$COMPOSE_CMD -f docker-compose.vps.yml exec -T backend python backend/manage.py import_all_data || echo "⚠️  Data import failed or already imported. Check logs."

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Test your API:"
echo "   curl http://localhost:8000/api/cars/"
echo ""
echo "📊 View logs:"
echo "   $COMPOSE_CMD -f docker-compose.vps.yml logs -f backend"
echo ""
echo "📋 Verify data:"
echo "   $COMPOSE_CMD -f docker-compose.vps.yml exec backend python backend/manage.py shell -c \"from cars.models import Car, Dealer; print(f'Cars: {Car.objects.count()}, Dealers: {Dealer.objects.count()}')\""
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD -f docker-compose.vps.yml down"
