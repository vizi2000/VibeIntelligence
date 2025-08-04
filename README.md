# Zenith Coder 🚀

An AI-powered development platform designed to transform chaotic development environments into organized, automated, and monetization-focused ecosystems.

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

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- PostgreSQL (via Docker)

### Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8100
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Docker Setup
```bash
docker-compose up -d
```

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

## 📝 Development Guidelines

This project follows the rules defined in:
- `DEVELOPMENT_RULES.md` - E2E testing requirements
- `GLOBAL_RULES.md` - System-wide deployment rules
- `DEPLOYMENT_REGISTRY.md` - Active deployment tracking

## 🤝 Contributing

See `CONTRIBUTING.md` for development guidelines and contribution process.

## 📄 License

MIT License - see LICENSE file for details.