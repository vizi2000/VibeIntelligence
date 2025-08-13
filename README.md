# Zenith Coder 🚀

An AI-powered development platform designed to transform chaotic development environments into organized, automated, and monetization-focused ecosystems.

## 🎉 Deployment Status

**DEPLOYED** - The Zenith Coder platform is now live with Docker containers! 

- **Backend API**: ✅ Healthy and running at `http://localhost/api/`
- **Frontend**: 🚧 Running but requires Traefik configuration fix
- **Database**: ✅ PostgreSQL running and healthy
- **Redis**: ✅ Running for caching
- **AI Services**: ✅ Integrated with OpenRouter and HuggingFace

Last deployment: 2025-08-04 03:30 CEST

## 🎯 Purpose

Zenith Coder is specifically built for developers (especially those with ADHD) to:
- Automatically organize and clean up project repositories
- Generate and maintain documentation using AI
- Track deployments and prevent port conflicts
- Identify duplicate projects and suggest consolidation
- Support project monetization strategies

## 📁 Project Structure

```
zenith-coder/
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   └── tests/            # Backend tests
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Frontend utilities
│   └── public/           # Static assets
├── database/             # Database files
│   ├── migrations/       # Database migrations
│   └── seeds/           # Seed data
├── scripts/             # Utility scripts
├── deployment/          # Deployment configurations
└── docs/               # Documentation
```

# VibeIntelligence (VI) 🚀

An AI-powered development platform designed to transform chaotic development environments into organized, automated, and monetization-focused ecosystems, all while adhering to vibecoding principles.

## 🎯 Purpose

VibeIntelligence is the central governance platform for our development ecosystem. It provides a unified dashboard to scan, analyze, document, and manage all software projects. 

Our core architectural strategy is to integrate VI with **`agent-zero`**, which serves as our foundational "Operating System" for all AI agent tasks. This allows VI to focus on its core domain of project management and UI, while `agent-zero` handles the complexities of agentic workflows.

## 🗺️ Roadmap & Status

The complete project vision, development roadmap, and current status are maintained in our living document:
- **[./ROADMAP.md](./ROADMAP.md)**

This document contains our sprint planning, bug tracker, and future enhancement list.

## 📁 Project Structure

```
vibe-intelligence/
├── backend/               # FastAPI backend
│   ├── src/
│   │   ├── api/          # API endpoints
│   │   ├── core/         # Core functionality
│   │   ├── models/       # Data models
│   │   ├── services/     # Business logic
│   │   └── utils/        # Utilities
│   └── tests/            # Backend tests
├── frontend/             # React TypeScript frontend
│   ├── src/
│   │   ├── components/   # React components
│   │   ├── pages/        # Page components
│   │   ├── services/     # API services
│   │   └── utils/        # Frontend utilities
│   └── public/           # Static assets
├── database/             # Database files
│   ├── migrations/       # Database migrations
│   └── seeds/           # Seed data
├── scripts/             # Utility scripts
├── deployment/          # Deployment configurations
└── docs/               # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Docker Setup (Recommended)
```bash
# This will build and run all services for a development environment
docker-compose up -d
```

### Manual Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8101

# Frontend
cd frontend
npm install
npm run dev
```

## 🔧 Configuration

Create a `.env` file in the root directory from the `.env.example` template. Key variables include:

```env
# Database
DATABASE_URL=postgresql://vi_user:vi_pass@localhost:5434/vi_db

# AI Services
OPENROUTER_API_KEY=your_key_here

# Application
API_PORT=8101
FRONTEND_PORT=3101
```

## 🚢 Production Deployment

The production environment uses Traefik as a reverse proxy.

```bash
# Build and deploy all services for production
docker-compose -f docker-compose.prod.yml up -d --build

# Check deployment status
docker ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

## 📝 Development Guidelines

This project follows the rules defined in the global constitution and its own internal documentation:
- `../docs/constitution/README.md` - The global "Zenith Coder" constitution.
- `CLAUDE.md` - Specific instructions for AI agents working in this repository.

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines and contribution process.

## 📄 License

MIT License - see LICENSE file for details.


## 🛠️ Current Status

### ✅ Completed
- Project inventory scanner (350 projects analyzed)
- Duplicate detection system (122 duplicate groups found)
- Organization report generation
- Backup scripts for safety

### 🔄 In Progress
- Setting up project structure
- FastAPI backend implementation
- PostgreSQL database schema

### 📋 Upcoming
- React dashboard development
- AI integration for documentation
- Deployment automation
- Task management system

## 📊 Key Findings

From the initial scan of the AI projects folder:
- **Total Projects**: 350
- **Total Size**: 19.56 GB
- **Duplicate Groups**: 122
- **Undocumented Projects**: 180
- **Active Deployments**: 14 (per DEPLOYMENT_REGISTRY.md)

Major duplicate issue: 18 versions of Xpress Delivery project scattered across folders.

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://zenith:zenith@localhost:5434/zenith_coder

# AI Services
OPENAI_API_KEY=your_key_here
CLAUDE_API_KEY=your_key_here

# GitHub
GITHUB_TOKEN=your_token_here

# Application
APP_PORT=8100
FRONTEND_PORT=3100
```

## 🚢 Production Deployment

### Using Docker Compose (Recommended)

The application uses Traefik as a reverse proxy to avoid port conflicts:

```bash
# Build and deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Check deployment status
docker ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop deployment
docker-compose -f docker-compose.prod.yml down
```

### Access Points
- **Frontend**: http://localhost/
- **Backend API**: http://localhost/api/
- **API Documentation**: http://localhost/api/docs
- **Traefik Dashboard**: http://localhost:8080/

### Health Checks
```bash
# Check backend health
curl http://localhost/api/health

# Check all container status
docker ps --format "table {{.Names}}\t{{.Status}}"
```

## 📝 Development Guidelines

This project follows the rules defined in:
- `DEVELOPMENT_RULES.md` - E2E testing requirements
- `GLOBAL_RULES.md` - System-wide deployment rules
- `DEPLOYMENT_REGISTRY.md` - Active deployment tracking
- `general_rules_v4.md` - Vibecoding principles

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines and contribution process.

## 📄 License

MIT License - see LICENSE file for details.