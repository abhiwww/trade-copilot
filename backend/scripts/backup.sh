#!/bin/bash
# PostgreSQL Backup Script for Trade Copilot
# Usage: ./backup.sh [database_name]

DB_NAME=${1:-tradecopilot}
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p "$BACKUP_DIR"

echo "Starting backup for database: $DB_NAME..."
# Use docker exec to run pg_dump inside the container
docker exec trade-copilot-postgres pg_dump -U trade $DB_NAME > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "Backup successful: $BACKUP_FILE"
else
    echo "Backup failed!"
    exit 1
fi
