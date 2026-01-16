#!/bin/bash
# Export Data as JSON Fixtures
# Usage: ./scripts/export_data.sh

set -e

EXPORT_DIR="./exports"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$EXPORT_DIR"

echo "📦 Exporting data to JSON fixtures..."

# Check if Docker is running
if ! docker compose ps web > /dev/null 2>&1; then
    echo "❌ Error: Web container is not running!"
    echo "Please start your Docker containers first: docker compose up -d"
    exit 1
fi

# Export all car-related data
echo "Exporting cars data..."
docker compose exec web python backend/manage.py dumpdata cars > "$EXPORT_DIR/cars_data_${DATE}.json"

# Export specific models separately (optional)
echo "Exporting dealers..."
docker compose exec web python backend/manage.py dumpdata cars.Dealer > "$EXPORT_DIR/dealers_${DATE}.json"

echo "Exporting cars..."
docker compose exec web python backend/manage.py dumpdata cars.Car > "$EXPORT_DIR/cars_${DATE}.json"

echo "Exporting car images..."
docker compose exec web python backend/manage.py dumpdata cars.CarImage > "$EXPORT_DIR/car_images_${DATE}.json"

echo "✅ Export completed!"
echo "📁 Files saved in: $EXPORT_DIR"
ls -lh "$EXPORT_DIR"/*_${DATE}.json

echo ""
echo "💡 To import on production:"
echo "   python backend/manage.py loaddata $EXPORT_DIR/cars_data_${DATE}.json"
