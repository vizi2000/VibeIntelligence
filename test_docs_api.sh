#!/bin/bash

echo "🧪 Testing Documentation Generation API"
echo "======================================="

# Get project list
echo -e "\n1. Getting project list..."
PROJECTS=$(curl -s http://localhost:8101/api/v1/projects/)
PROJECT_ID=$(echo $PROJECTS | jq -r '.[0].id')
PROJECT_NAME=$(echo $PROJECTS | jq -r '.[0].name')

if [ -z "$PROJECT_ID" ]; then
    echo "❌ No projects found"
    exit 1
fi

echo "✅ Found project: $PROJECT_NAME (ID: $PROJECT_ID)"

# Generate documentation
echo -e "\n2. Starting documentation generation..."
RESPONSE=$(curl -s -X POST http://localhost:8101/api/v1/documentation/generate \
  -H "Content-Type: application/json" \
  -d "{\"project_id\": $PROJECT_ID, \"doc_type\": \"readme\"}")

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
echo "✅ Task created: $TASK_ID"
echo "📝 Response: $RESPONSE"

# Poll for completion
echo -e "\n3. Waiting for completion..."
MAX_ATTEMPTS=30
ATTEMPT=0

while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
    sleep 2
    STATUS_RESPONSE=$(curl -s http://localhost:8101/api/v1/documentation/status/$TASK_ID)
    STATUS=$(echo $STATUS_RESPONSE | jq -r '.status')
    
    echo -n "   Attempt $((ATTEMPT + 1)): Status = $STATUS"
    
    if [ "$STATUS" = "completed" ]; then
        echo " ✅"
        echo -e "\n✅ Documentation generated successfully!"
        
        # Get the documentation content
        DOC_CONTENT=$(echo $STATUS_RESPONSE | jq -r '.result.documentation')
        FILE_PATH=$(echo $STATUS_RESPONSE | jq -r '.result.file_path')
        
        echo -e "\n📄 Generated file: $FILE_PATH"
        echo -e "\n📝 Documentation preview (first 500 chars):"
        echo "========================================="
        echo "$DOC_CONTENT" | head -c 500
        echo -e "\n========================================="
        
        # Get all documents for this project
        echo -e "\n4. Fetching all project documentation..."
        DOCS=$(curl -s http://localhost:8101/api/v1/documentation/project/$PROJECT_ID)
        DOC_COUNT=$(echo $DOCS | jq '.documents | length')
        echo "✅ Found $DOC_COUNT documents for this project"
        
        exit 0
    elif [ "$STATUS" = "failed" ]; then
        echo " ❌"
        ERROR=$(echo $STATUS_RESPONSE | jq -r '.error')
        echo "❌ Documentation generation failed: $ERROR"
        exit 1
    else
        echo ""
    fi
    
    ATTEMPT=$((ATTEMPT + 1))
done

echo -e "\n❌ Timeout: Documentation generation did not complete in time"
exit 1