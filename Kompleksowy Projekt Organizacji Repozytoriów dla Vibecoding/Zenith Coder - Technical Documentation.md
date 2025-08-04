# Zenith Coder - Technical Documentation

## 🚀 Project Overview

**Zenith Coder** is an AI-powered development platform designed to transform chaotic development environments into organized, automated, and monetization-focused ecosystems. Built specifically for developers with ADHD, it provides intelligent project organization, automated documentation generation, task management, and monetization support.

## 🏗️ Architecture Overview

### System Architecture

Zenith Coder follows a modern microservices architecture with the following components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   AI Services   │
│   (React)       │◄──►│   (FastAPI)     │◄──►│  (Multi-Model)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Nginx       │    │   PostgreSQL    │    │   Vector DB     │
│  (Reverse Proxy)│    │   (Main DB)     │    │   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Traefik      │    │     Redis       │    │   External      │
│ (Load Balancer) │    │    (Cache)      │    │   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack

#### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **shadcn/ui** for component library
- **Lucide React** for icons
- **Recharts** for data visualization
- **Framer Motion** for animations

#### Backend
- **FastAPI** (Python 3.11) for REST API
- **SQLAlchemy** for ORM
- **Alembic** for database migrations
- **Pydantic** for data validation
- **AsyncIO** for asynchronous operations

#### AI Integration
- **OpenAI GPT-4o** for general reasoning
- **Anthropic Claude 3.5 Sonnet** for code generation
- **Google Gemini Pro** for analysis
- **OpenRouter** for model routing
- **Hugging Face** for specialized models

#### Infrastructure
- **PostgreSQL 15** for primary database
- **Redis 7** for caching and sessions
- **ChromaDB** for vector storage
- **Docker & Docker Compose** for containerization
- **Traefik** for reverse proxy and SSL
- **Nginx** for static file serving

## 📊 Database Schema

### Core Tables

#### Projects
```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status project_status DEFAULT 'planning',
    priority task_priority DEFAULT 'medium',
    health_score INTEGER CHECK (health_score >= 0 AND health_score <= 100),
    docs_progress INTEGER CHECK (docs_progress >= 0 AND docs_progress <= 100),
    github_url VARCHAR(500),
    local_path VARCHAR(500),
    tags TEXT[],
    revenue DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Tasks
```sql
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status task_status DEFAULT 'todo',
    priority task_priority DEFAULT 'medium',
    estimated_duration INTEGER,
    actual_duration INTEGER,
    tags TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### AI Interactions
```sql
CREATE TABLE ai_interactions (
    id UUID PRIMARY KEY,
    project_id UUID REFERENCES projects(id),
    interaction_type VARCHAR(100) NOT NULL,
    model_used VARCHAR(100) NOT NULL,
    prompt TEXT NOT NULL,
    response TEXT NOT NULL,
    tokens_used INTEGER,
    cost DECIMAL(8,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 🤖 AI Orchestrator

### Model Selection Strategy

The AI Orchestrator implements intelligent model routing based on task type:

```python
model_routing_rules = {
    TaskType.CODE_GENERATION: [
        "anthropic/claude-3-5-sonnet-20241022",  # Best for code
        "openai/gpt-4o",
        "google/gemini-pro"
    ],
    TaskType.GENERAL_REASONING: [
        "openai/gpt-4o",  # Best for reasoning
        "anthropic/claude-3-5-sonnet-20241022",
        "google/gemini-pro"
    ],
    TaskType.SUMMARIZATION: [
        "openai/gpt-4o-mini",  # Cost-effective
        "anthropic/claude-3-haiku-20240307",
        "google/gemini-pro"
    ]
}
```

### AI Agents

#### 1. Documentation Agent
- **Purpose**: Generates comprehensive project documentation
- **Capabilities**: README files, API docs, code comments
- **Model**: Claude 3.5 Sonnet (best for structured writing)

#### 2. Task Manager Agent
- **Purpose**: Breaks down projects into manageable tasks
- **Capabilities**: ADHD-friendly task decomposition, priority setting
- **Model**: GPT-4o (excellent reasoning for task planning)

#### 3. Monetization Agent
- **Purpose**: Identifies revenue opportunities
- **Capabilities**: Market analysis, pricing strategies, platform recommendations
- **Model**: GPT-4o (best for business analysis)

#### 4. Skill Analyst Agent
- **Purpose**: Analyzes developer skills and suggests improvements
- **Capabilities**: Skill gap analysis, learning path recommendations
- **Model**: Claude 3.5 Sonnet (detailed analysis capabilities)

## 🔧 API Endpoints

### Core API Routes

#### Projects
```
GET    /api/v1/projects/           # List all projects
POST   /api/v1/projects/           # Create new project
GET    /api/v1/projects/{id}       # Get project details
PUT    /api/v1/projects/{id}       # Update project
DELETE /api/v1/projects/{id}       # Delete project
POST   /api/v1/projects/{id}/scan  # Scan project directory
```

#### Tasks
```
GET    /api/v1/tasks/              # List all tasks
POST   /api/v1/tasks/              # Create new task
GET    /api/v1/tasks/{id}          # Get task details
PUT    /api/v1/tasks/{id}          # Update task
DELETE /api/v1/tasks/{id}          # Delete task
POST   /api/v1/tasks/{id}/complete # Mark task as complete
```

#### AI Assistant
```
POST   /api/v1/ai/chat             # Chat with AI assistant
POST   /api/v1/ai/analyze          # Analyze project/code
POST   /api/v1/ai/generate-docs    # Generate documentation
POST   /api/v1/ai/suggest-tasks    # Suggest tasks for project
GET    /api/v1/ai/models           # List available AI models
```

#### Monetization
```
GET    /api/v1/monetization/opportunities     # List opportunities
POST   /api/v1/monetization/analyze          # Analyze project for monetization
GET    /api/v1/monetization/freelance        # Find matching freelance jobs
POST   /api/v1/monetization/track-revenue    # Track revenue from project
```

## 🚀 Deployment

### Docker Deployment

The project uses Docker Compose for easy deployment:

```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
  
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/zenith
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=zenith_coder
      - POSTGRES_USER=zenith_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
```

### Environment Configuration

Required environment variables:

```bash
# Database
DATABASE_URL=postgresql://zenith_user:password@localhost:5432/zenith_coder
REDIS_URL=redis://localhost:6379

# AI API Keys
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
OPENROUTER_API_KEY=sk-or-...
HUGGINGFACE_API_TOKEN=hf_...

# Security
SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256

# Features
ENABLE_EXPERIMENTAL_FEATURES=false
ENABLE_AUTO_DOCS=true
ENABLE_FREELANCE_FINDER=true
```

## 🔒 Security Considerations

### Authentication & Authorization
- JWT-based authentication
- API key protection for AI services
- Rate limiting on API endpoints
- CORS configuration for frontend access

### Data Protection
- Encrypted storage of API keys
- Secure database connections
- Input validation and sanitization
- SQL injection prevention via ORM

### AI Safety
- Prompt injection protection
- Content filtering for AI responses
- Token usage monitoring
- Cost controls for AI API calls

## 📈 Performance Optimization

### Caching Strategy
- Redis for session storage
- API response caching
- Database query optimization
- Static asset caching via Nginx

### Database Optimization
- Proper indexing on frequently queried columns
- Connection pooling
- Query optimization
- Periodic maintenance tasks

### AI Performance
- Model response caching
- Batch processing for multiple requests
- Fallback models for high availability
- Token usage optimization

## 🧪 Testing Strategy

### Unit Tests
- Backend API endpoints
- AI orchestrator logic
- Database models and queries
- Utility functions

### Integration Tests
- Frontend-backend communication
- AI model integrations
- Database operations
- External API connections

### End-to-End Tests
- Complete user workflows
- Dashboard functionality
- AI assistant interactions
- Project management features

## 📊 Monitoring & Logging

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking
- User activity logging

### AI Usage Monitoring
- Token consumption tracking
- Model performance metrics
- Cost analysis
- Response quality assessment

### Infrastructure Monitoring
- Container health
- Database performance
- Memory and CPU usage
- Network connectivity

## 🔄 Development Workflow

### Git Workflow
- Feature branch development
- Pull request reviews
- Automated testing on CI/CD
- Semantic versioning

### Code Quality
- ESLint for JavaScript/TypeScript
- Black for Python formatting
- Pre-commit hooks
- Code coverage requirements

### Documentation
- Automated API documentation
- Code comments and docstrings
- Architecture decision records
- User guides and tutorials

## 🚧 Future Enhancements

### Phase 2 Features
- Real-time collaboration
- Advanced AI model fine-tuning
- Mobile application
- Plugin system for extensibility

### Integration Roadmap
- GitHub Actions integration
- Slack/Discord notifications
- Jira/Trello synchronization
- Cloud deployment automation

### AI Capabilities
- Custom model training
- Voice interface
- Code review automation
- Predictive analytics

## 📞 Support & Maintenance

### Backup Strategy
- Daily database backups
- Configuration backups
- Docker image versioning
- Disaster recovery procedures

### Update Process
- Rolling updates for zero downtime
- Database migration procedures
- Configuration management
- Rollback procedures

### Troubleshooting
- Common issues and solutions
- Log analysis procedures
- Performance debugging
- AI model fallback procedures

---

This technical documentation provides a comprehensive overview of the Zenith Coder platform. For specific implementation details, refer to the individual module documentation and code comments.

