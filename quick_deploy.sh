#!/bin/bash

# Quick deployment script for VibeIntelligence
echo "🚀 Quick deployment to vizi@borgtools.ddns.net"

# Connect to server and run deployment
ssh vizi@borgtools.ddns.net << 'EOF'
cd ~/vibeintelligence

# Start containers without building (pull from registry if needed)
echo "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

echo "Waiting for services..."
sleep 10

# Check status
docker-compose -f docker-compose.prod.yml ps
echo ""
echo "✅ Deployment initiated!"
echo "Note: First deployment may take 10-15 minutes to build containers."
echo ""
echo "Check status with:"
echo "  ssh vizi@borgtools.ddns.net 'cd ~/vibeintelligence && docker-compose -f docker-compose.prod.yml ps'"
echo ""
echo "View logs with:"
echo "  ssh vizi@borgtools.ddns.net 'cd ~/vibeintelligence && docker-compose -f docker-compose.prod.yml logs -f'"
EOF