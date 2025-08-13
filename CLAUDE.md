# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python/FastAPI)
```bash
# Navigate to backend directory
cd backend

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server (development)
uvicorn src.main:app --reload --port 8100

# Run single test
pytest tests/test_scanner.py::test_scan_endpoint -v

# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Linting and formatting
black src/ tests/
ruff check src/ tests/
```

### Frontend (React/TypeScript/Vite)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev  # Runs on http://localhost:5173

# Build for production
npm run build

# Run linting
npm run lint

# Run tests
npm run test
npm run test:coverage
```

### Docker Commands
```bash
# Start all services (development)
docker-compose up -d

# Start services with rebuild
docker-compose up -d --build

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Access database
docker exec -it zenith_postgres psql -U zenith -d zenith_coder

# Run database migrations in container
docker exec zenith_backend python -m alembic upgrade head

# Clean restart (remove volumes)
docker-compose down -v
docker-compose up -d --build

# Production deployment
docker-compose -f docker-compose.prod.yml up -d --build
```

### Installation Script
```bash
# Interactive installation
./install.sh

# Quick installation with defaults
./install.sh --quick

# Check system status
./install.sh --status
```

## High-Level Architecture

### System Purpose
VibeIntelligence (VI) is an AI-powered development platform that organizes chaotic development environments through automated project discovery, analysis, documentation generation, and deployment management. The platform follows "Vibecoding" v4.0 principles with a focus on ADHD-friendly UI and developer wellbeing.

### Multi-Agent Architecture
The system uses specialized AI agents coordinated through an `AgentManager`:
- **Scanner Agent**: Discovers projects using filesystem analysis and pattern matching
- **Analyzer Agent**: Evaluates code quality, health scores, and technical debt
- **Documentation Agent**: Generates README files and API documentation
- **Deployment Agent**: Manages Docker deployments and port conflict resolution
- **Task Suggester Agent**: Provides AI-powered development recommendations

Each agent inherits from `BaseAgent` and implements the `process_task()` method for asynchronous task processing.

### Service Layer Architecture
```
Frontend (React) → Nginx Proxy → FastAPI Backend → Services → Database/AI
                                                  ↓
                                            Agent Manager
                                                  ↓
                                         Individual Agents → AI Services
```

Key services:
- `ProjectService`: Manages project CRUD operations and scanning
- `ScannerService`: Coordinates filesystem scanning operations
- `DeploymentService`: Handles Docker deployment management
- `AIService`: Interfaces with OpenRouter/HuggingFace for AI operations
- `AgentManager`: Orchestrates multi-agent task execution

### Data Flow Patterns

#### Scanning Workflow
1. User triggers scan via `/api/v1/scanner/scan` endpoint
2. `ScannerService` initiates filesystem traversal from `/ai_projects`
3. Projects identified by indicators (package.json, requirements.txt, etc.)
4. Each project analyzed for health score, tech stack, dependencies
5. Results stored in PostgreSQL with async task status updates
6. Frontend polls `/api/v1/scanner/status/{task_id}` for completion

#### Agent Task Processing
1. Task created with status "pending" in database
2. `AgentManager` assigns task to appropriate agent
3. Agent processes task asynchronously (status: "processing")
4. Results stored in task record (status: "completed" or "failed")
5. Frontend receives updates via polling or WebSocket

### Configuration & Environment

Key environment variables (from `.env`):
- `DATABASE_URL`: PostgreSQL connection (default: postgresql://zenith:zenith@localhost:5434/zenith_coder)
- `REDIS_URL`: Redis cache connection
- `OPENROUTER_API_KEY`: Primary AI service authentication
- `AI_PROJECTS_PATH`: Root directory for project scanning (container: /ai_projects, host: /Users/wojciechwiesner/ai)

Port mappings:
- Backend API: 8100 (development), 80/443 (production via Traefik)
- Frontend: 5173 (Vite dev), 3000 (production)
- PostgreSQL: 5434
- Redis: 6381

### Database Schema Patterns

SQLAlchemy models use these patterns:
- UUID primary keys for distributed systems compatibility
- Timestamps (created_at, updated_at) on all models
- Soft deletes via `is_active` flags
- JSON columns for flexible metadata storage
- Async session management with context managers

### AI Integration Strategy

The platform integrates with `agent-zero` framework:
1. VI focuses on UI and project management
2. Complex agent tasks delegated to `agent-zero`
3. Communication via standardized task queue
4. Results synchronized back to VI database

AI model selection (via `core/config.py`):
- Default: `openrouter/horizon-beta` for all agent tasks
- Fallback: HuggingFace models for cost optimization
- Local model support via `ENABLE_LOCAL_MODELS` flag