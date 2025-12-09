#!/bin/bash
set -e

echo "Starting rollback..."

LATEST_BACKUP=$(ls -td ~/QApp_backup_* | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "No backup found. Rollback failed."
    exit 1
fi

rm -rf ~/QApp
mv "$LATEST_BACKUP" ~/QApp

echo "Rollback completed successfully."
