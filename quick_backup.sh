#!/bin/bash

# Quick automated backup script

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SOURCE_DIR="/Users/wojciechwiesner/ai"
BACKUP_DIR="/Users/wojciechwiesner/ai_backup_${TIMESTAMP}"

echo "Starting quick backup of AI folder..."
echo "This will create a backup at: ${BACKUP_DIR}"

# Create a tar archive excluding common large/unnecessary files
tar -czf "${BACKUP_DIR}.tar.gz" \
    --exclude='node_modules' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='.DS_Store' \
    --exclude='*.log' \
    --exclude='.next' \
    --exclude='build' \
    --exclude='dist' \
    --exclude='target' \
    -C /Users/wojciechwiesner ai

if [ $? -eq 0 ]; then
    SIZE=$(ls -lh "${BACKUP_DIR}.tar.gz" | awk '{print $5}')
    echo "✅ Backup completed successfully!"
    echo "Backup file: ${BACKUP_DIR}.tar.gz"
    echo "Size: ${SIZE}"
else
    echo "❌ Backup failed!"
    exit 1
fi