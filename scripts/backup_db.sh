#!/bin/bash
# Database Backup Script
# Usage: ./scripts/backup_db.sh

set -e

# Configuration
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

DB_NAME=${POSTGRES_DB:-mydb}
DB_USER=${POSTGRES_USER:-myuser}

echo "📦 Starting database backup..."
echo "Database: $DB_NAME"
echo "User: $DB_USER"
echo "Timestamp: $TIMESTAMP"

# Check if Docker is running
if ! docker compose ps db > /dev/null 2>&1; then
    echo "❌ Error: Database container is not running!"
    echo "Please start your Docker containers first: docker compose up -d"
    exit 1
fi

# Create backup
BACKUP_FILE="$BACKUP_DIR/backup_${DATE}.sql"
echo "Creating backup: $BACKUP_FILE"

docker compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$BACKUP_FILE"

# Compress backup
if command -v gzip &> /dev/null; then
    echo "Compressing backup..."
    gzip "$BACKUP_FILE"
    BACKUP_FILE="${BACKUP_FILE}.gz"
fi

# Get file size
FILE_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo "✅ Backup completed successfully!"
echo "📁 File: $BACKUP_FILE"
echo "📊 Size: $FILE_SIZE"

# Keep only last 7 days of backups
echo "🧹 Cleaning old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "backup_*.sql*" -mtime +7 -delete

# List remaining backups
echo ""
echo "📋 Remaining backups:"
ls -lh "$BACKUP_DIR"/backup_*.sql* 2>/dev/null || echo "No backups found"

echo ""
echo "💡 To restore:"
echo "   docker compose exec -T db psql -U $DB_USER $DB_NAME < $BACKUP_FILE"
