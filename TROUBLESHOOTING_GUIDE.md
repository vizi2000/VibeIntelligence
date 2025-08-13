# Zenith Coder Troubleshooting Guide

## Complete Issue Documentation and Fixes

### 1. Frontend Port 3101 Not Accessible

**Issue**: Frontend was not accessible on http://localhost:3101

**Root Causes**:
1. Docker-compose port mapping was incorrect (3101:3000 instead of 3101:80)
2. Nginx was serving on port 80, not 3000

**Fix Applied**:
```yaml
# docker-compose.yml
frontend:
  ports:
    - "3101:80"  # Changed from 3101:3000
```

**Status**: ✅ FIXED

---

### 2. Session Management Errors

**Issue**: "Instance <AgentTask> is not bound to a Session" errors

**Root Cause**: SQLAlchemy sessions were being detached when passed between functions

**Fix Applied**:
```python
# backend/src/agents/base_agent.py
task = db.merge(task)  # Re-attach task to session
```

**Status**: ✅ FIXED

---

### 3. Async For Statement Errors

**Issue**: "'async for' requires an object with __aiter__ method, got generator"

**Root Cause**: `get_db()` is a synchronous generator, not async

**Fix Applied**:
```python
# Changed throughout codebase
# From: async for db in get_db():
# To: db = SessionLocal()
```

**Files Fixed**:
- `/backend/src/services/agent_manager.py`
- `/backend/src/agents/base_agent.py`
- `/backend/src/agents/scanner_agent.py`
- All other agent files

**Status**: ✅ FIXED

---

### 4. AI Chat Error - TaskType.GENERAL Not Found

**Issue**: "TaskType.GENERAL doesn't exist"

**Root Cause**: Incorrect task type enum value

**Fix Applied**:
```python
# backend/src/services/ai_service.py
task_type=TaskType.GENERAL_CHAT  # Changed from TaskType.GENERAL
```

**Status**: ✅ FIXED

---

### 5. Scanner Path Issues in Docker

**Issue**: Scanner couldn't find projects - path mismatch between host and container

**Root Cause**: Host paths (/Users/wojciechwiesner/ai) don't exist in Docker container

**Fixes Applied**:

1. Updated config paths:
```python
# backend/src/core/config.py
ai_projects_path: str = "/ai_projects"  # Changed from local path
```

2. Added path conversion in scanner API:
```python
# backend/src/api/scanner.py
if scan_path and scan_path.startswith("/Users/"):
    scan_path = scan_path.replace("/Users/wojciechwiesner/ai", "/ai_projects")
```

**Status**: ✅ FIXED

---

### 6. Projects API Validation Errors

**Issue**: "Input should be a valid string" for project_type field

**Root Cause**: NULL values in database for required fields

**Fix Applied**:
```sql
UPDATE projects SET project_type = 'Unknown' WHERE project_type IS NULL;
```

**Status**: ✅ FIXED

---

### 7. Frontend API Integration Issues

**Issue**: API calls returning 404, frontend not using correct environment variables

**Root Causes**:
1. Vite requires `VITE_` prefix for env vars, not `REACT_APP_`
2. Environment variables not available during Docker build
3. Nginx proxy configuration incorrect

**Fixes Applied**:

1. Updated docker-compose.yml:
```yaml
frontend:
  build:
    args:
      VITE_API_URL: /api/v1
```

2. Updated Dockerfile to accept build args:
```dockerfile
ARG VITE_API_URL=/api/v1
ENV VITE_API_URL=$VITE_API_URL
```

3. Updated nginx.conf:
```nginx
location /api/ {
    proxy_pass http://backend:8100/api/;
    proxy_set_header Host $http_host;
    proxy_set_header X-Forwarded-Host $http_host;
}
```

**Status**: ✅ FIXED

---

### 8. FastAPI Redirect Issues

**Issue**: API redirects (307) going to wrong host (localhost:80 instead of localhost:3101)

**Root Cause**: FastAPI not properly handling proxy headers

**Fix Applied**:

1. Created proxy middleware:
```python
# backend/src/middleware/proxy.py
class ProxyHeadersMiddleware(BaseHTTPMiddleware):
    # Handles X-Forwarded headers
```

2. Added to FastAPI app:
```python
app.add_middleware(ProxyHeadersMiddleware)
```

**Status**: ✅ FIXED

---

### 9. Datetime JSON Serialization Error

**Issue**: "Object of type datetime is not JSON serializable" when scanning

**Root Cause**: Scanner results contain datetime objects that can't be serialized to JSON

**Fix Applied**:
```python
# backend/src/services/scanner_service.py
def _serialize_datetime(self, obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    # Recursive handling for dicts and lists

# Use before JSON serialization
serialized_result = self._serialize_datetime(result)
scan.result_data = json.dumps(serialized_result)
```

**Status**: ✅ FIXED

---

### 10. AI Service Task Type Error in Scanner

**Issue**: "analysis" is not a valid task type

**Root Cause**: Using string instead of TaskType enum

**Fix Applied**:
```python
# backend/src/services/project_scanner.py
from ..ai import TaskType

response = await ai_service.orchestrator.generate(
    prompt=prompt,
    task_type=TaskType.CODE_ANALYSIS,  # Changed from "analysis"
    max_tokens=300
)
```

**Status**: ✅ FIXED

---

## Current Issues That Need Fixing

### 11. Health Score Shows as NaN%

**Issue**: All projects display "Health: NaN%"

**Root Cause**: Health score is null or undefined in the database

**Proposed Fix**:
1. Ensure health_score is calculated during scanning
2. Set default value for existing projects
3. Update frontend to handle null values gracefully

**Status**: ❌ PENDING

---

### 12. Missing Dashboard Components

**Issue**: AI Assistant and Agent Activity cards not showing on dashboard

**Root Cause**: Dashboard component was rewritten but some parts were lost

**What's Missing**:
- AI Assistant card with chat preview
- Agent Activity card with task status
- System statistics

**Status**: ❌ PENDING

---

### 13. Missing API Endpoints

**Issue**: `/api/v1/health` and `/api/v1/agents/stats` return 404

**Root Cause**: Endpoints not implemented

**Required Implementation**:
- Health check endpoint
- Agent statistics endpoint

**Status**: ❌ PENDING

---

### 14. Scan Results Not Visible

**Issue**: Scan completes but no visible changes to the scanned project

**Root Cause**: 
1. Health score not being updated
2. UI not showing what was discovered
3. No visual feedback for scan results

**Status**: ❌ PENDING

---

## Knowledge Database Entry

This documentation should be saved in the project's CLAUDE.md file for future reference:

```markdown
# Zenith Coder Knowledge Base

## Common Issues and Solutions

### Docker Path Issues
- Container uses `/ai_projects` not `/Users/wojciechwiesner/ai`
- Scanner API automatically converts paths

### Frontend Environment Variables
- Use `VITE_` prefix, not `REACT_APP_`
- Pass as build args in docker-compose

### SQLAlchemy Session Issues
- Use `db.merge()` to reattach detached objects
- Don't use `async for` with `get_db()`

### API Proxy Issues
- Nginx must forward proper headers
- FastAPI needs ProxyHeadersMiddleware
- Use trailing slashes consistently

### Datetime Serialization
- Convert datetime objects to ISO strings before JSON serialization
- Use custom serializer function

## Testing Commands

# Run comprehensive test
node comprehensive_test.js

# Test scanning visually
node test_scan_visual.js

# Check API directly
curl http://localhost:8101/api/v1/projects/
```