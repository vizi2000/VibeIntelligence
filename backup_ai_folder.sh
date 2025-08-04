#!/bin/bash

# Backup script for AI folder
# Creates a timestamped backup excluding large unnecessary files

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SOURCE_DIR="/Users/wojciechwiesner/ai"
BACKUP_DIR="/Users/wojciechwiesner/ai_backup_${TIMESTAMP}"
EXCLUDE_FILE="/Users/wojciechwiesner/ai/zenith coder/backup_exclude.txt"

echo "========================================"
echo "AI Folder Backup Script"
echo "========================================"
echo "Timestamp: ${TIMESTAMP}"
echo "Source: ${SOURCE_DIR}"
echo "Destination: ${BACKUP_DIR}"
echo ""

# Create exclude file with patterns to skip
cat > "${EXCLUDE_FILE}" << EOF
node_modules/
.git/
*.pyc
__pycache__/
.venv/
venv/
.env
.DS_Store
*.log
*.tmp
.next/
build/
dist/
target/
out/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
EOF

echo "Exclusion patterns created."
echo ""

# Show estimated size
echo "Calculating backup size (this may take a moment)..."
TOTAL_SIZE=$(du -sh "${SOURCE_DIR}" 2>/dev/null | cut -f1)
echo "Total source size: ${TOTAL_SIZE}"

# Estimate size without excluded patterns
BACKUP_SIZE=$(rsync -an --stats --exclude-from="${EXCLUDE_FILE}" "${SOURCE_DIR}/" "${BACKUP_DIR}/" 2>/dev/null | grep "Total file size" | awk '{print $4}')
echo "Estimated backup size: ${BACKUP_SIZE}"
echo ""

# Ask for confirmation
read -p "Do you want to proceed with the backup? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Starting backup..."
    echo ""
    
    # Create backup using rsync with progress
    rsync -av --progress --exclude-from="${EXCLUDE_FILE}" "${SOURCE_DIR}/" "${BACKUP_DIR}/"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ Backup completed successfully!"
        echo "Backup location: ${BACKUP_DIR}"
        
        # Create backup info file
        cat > "${BACKUP_DIR}/BACKUP_INFO.txt" << EOF
AI Folder Backup Information
============================
Backup Date: $(date)
Source Directory: ${SOURCE_DIR}
Backup Directory: ${BACKUP_DIR}
Total Projects Backed Up: $(find "${BACKUP_DIR}" -name "package.json" -o -name "requirements.txt" -o -name "Dockerfile" | wc -l)

Excluded Patterns:
$(cat "${EXCLUDE_FILE}")

Backup created by Zenith Coder organization process.
EOF
        
        # Calculate final backup size
        FINAL_SIZE=$(du -sh "${BACKUP_DIR}" 2>/dev/null | cut -f1)
        echo "Final backup size: ${FINAL_SIZE}"
        
        # Create verification script
        cat > "${BACKUP_DIR}/verify_backup.sh" << 'VERIFY_EOF'
#!/bin/bash
echo "Verifying backup integrity..."
find . -type f -name "*.json" -o -name "*.py" -o -name "*.js" -o -name "*.tsx" | wc -l
echo "Total source files found."
VERIFY_EOF
        chmod +x "${BACKUP_DIR}/verify_backup.sh"
        
    else
        echo "❌ Backup failed! Please check the error messages above."
        exit 1
    fi
else
    echo "Backup cancelled."
    exit 0
fi

# Clean up
rm -f "${EXCLUDE_FILE}"

echo ""
echo "Backup process complete!"