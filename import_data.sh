#!/bin/bash
# Data Import Script for VPS Deployment
# This script imports all CSV data into the database

set -e

echo "📊 CarsDedo Data Import"
echo "======================="

# Check if we're in a Docker container or running locally
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "🐳 Running inside Docker container"
    MANAGE_CMD="python backend/manage.py"
else
    echo "💻 Running locally"
    MANAGE_CMD="docker compose -f docker-compose.vps.yml exec backend python backend/manage.py"
fi

echo ""
echo "🔄 Importing all data from CSV files..."
echo ""

# Run the import_all_data management command
$MANAGE_CMD import_all_data

echo ""
echo "✅ Data import completed!"
echo ""
echo "📋 Verify data:"
echo "   $MANAGE_CMD shell -c \"from cars.models import Car, Dealer; print(f'Cars: {Car.objects.count()}, Dealers: {Dealer.objects.count()}')\""
