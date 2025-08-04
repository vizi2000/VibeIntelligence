# Zenith Coder - User Guide

## 🌟 Welcome to Zenith Coder

Congratulations on taking the first step toward becoming a **top vibecoder**! Zenith Coder is your AI-powered development companion, designed specifically to help developers with ADHD (and anyone who wants better organization) transform chaotic development environments into streamlined, profitable ecosystems.

## 🎯 What Zenith Coder Does For You

### 🧹 **Project Organization**
- Automatically scans and organizes your local projects
- Identifies duplicate files and unused dependencies
- Creates consistent project structures
- Syncs with GitHub repositories

### 📚 **AI-Powered Documentation**
- Generates comprehensive README files
- Creates API documentation automatically
- Maintains up-to-date project documentation
- Ensures every project has proper docs for AI agents

### 📋 **ADHD-Friendly Task Management**
- Breaks down large projects into manageable chunks
- Provides time estimates for each task
- Offers "quick wins" to maintain momentum
- Integrates Pomodoro technique for focus sessions

### 💰 **Monetization Support**
- Identifies revenue opportunities in your projects
- Suggests SaaS conversion strategies
- Finds matching freelance opportunities
- Tracks project profitability

### 🚀 **Deployment Management**
- Eliminates port conflicts with smart routing
- Provides one-click deployment solutions
- Manages Docker containers automatically
- Handles SSL certificates and domain management

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have:
- Docker and Docker Compose installed
- At least one AI API key (OpenAI, Claude, or Gemini)
- Git configured on your system
- Node.js 18+ (for development)

### Quick Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/zenith-coder.git
   cd zenith-coder
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and preferences
   ```

3. **Deploy with One Command**
   ```bash
   ./scripts/deploy.sh
   ```

4. **Access Your Dashboard**
   - Dashboard: http://localhost
   - API Docs: http://localhost/api/v1/docs
   - Traefik Dashboard: http://localhost:8080

## 🎮 Using the Dashboard

### 🏠 Dashboard Home

The main dashboard gives you an instant overview of your development ecosystem:

#### **Hero Section**
- Personalized greeting based on time of day
- Quick access to focus sessions and AI assistant
- Motivational messaging to maintain momentum

#### **Active Projects Panel**
Each project card shows:
- **Health Score** (0-100): Overall project quality
- **Documentation Progress**: Percentage of complete docs
- **Open Issues**: Number of problems to address
- **Next Task**: AI-suggested next action
- **Technology Tags**: Quick identification of tech stack
- **Priority Level**: Visual priority indicators

#### **AI Assistant Panel**
- Real-time suggestions based on project analysis
- Interactive chat interface
- Quick action buttons for common tasks
- Context-aware recommendations

#### **Monetization Insights Panel**
- Current month revenue tracking
- Identified opportunities with potential values
- Trending AI industry news
- Matching freelance job opportunities

### 🤖 AI Assistant

The AI Assistant is your intelligent development companion:

#### **Starting a Conversation**
1. Click on "AI Assistant" in the sidebar
2. Type your question or request
3. The AI will analyze your projects and provide contextual help

#### **Common Use Cases**
- **"Help me document my API project"**
  - AI analyzes your code structure
  - Generates OpenAPI specifications
  - Creates README with setup instructions
  - Provides usage examples

- **"What should I work on next?"**
  - Reviews all your projects
  - Considers deadlines and priorities
  - Suggests optimal task sequence
  - Provides time estimates

- **"How can I monetize my projects?"**
  - Analyzes market potential
  - Suggests business models
  - Identifies target audiences
  - Provides implementation roadmap

#### **AI Model Selection**
The system automatically chooses the best AI model for each task:
- **Code Generation**: Claude 3.5 Sonnet (best for structured code)
- **Analysis & Reasoning**: GPT-4o (excellent logical reasoning)
- **Documentation**: Claude 3.5 Sonnet (superior writing quality)
- **Quick Tasks**: GPT-4o-mini (cost-effective for simple tasks)

### 📁 Project Management

#### **Adding New Projects**
1. Click "Add New Project" on the dashboard
2. Choose between:
   - **Scan Local Directory**: Import existing project
   - **Create New**: Start fresh with templates
   - **Clone from GitHub**: Import remote repository

#### **Project Health Monitoring**
Each project receives a health score based on:
- **Documentation Quality** (30%): README, API docs, comments
- **Code Quality** (25%): Linting, testing, structure
- **Maintenance** (20%): Recent commits, issue resolution
- **Monetization Readiness** (15%): Market potential, completion
- **Security** (10%): Vulnerability scans, best practices

#### **Automated Project Cleanup**
Zenith Coder automatically:
- Removes duplicate files across projects
- Updates outdated dependencies
- Fixes common configuration issues
- Standardizes project structures
- Syncs with GitHub repositories

### 📋 Task Management

#### **ADHD-Optimized Features**
- **Time Boxing**: All tasks have estimated durations
- **Quick Wins**: Easy 5-15 minute tasks for momentum
- **Focus Sessions**: Integrated Pomodoro timer
- **Progress Visualization**: Clear completion indicators
- **Gentle Reminders**: Non-intrusive notifications

#### **Task Prioritization**
Tasks are automatically prioritized using:
1. **Deadlines**: Time-sensitive items first
2. **Impact**: High-value tasks prioritized
3. **Dependencies**: Blocking tasks elevated
4. **Energy Level**: Match task complexity to your current state
5. **Momentum**: Quick wins when motivation is low

#### **Pomodoro Integration**
1. Select a task from your focus list
2. Click "Start Pomodoro Session"
3. Work for 25 minutes with distraction blocking
4. Take a 5-minute break
5. Repeat cycle with automatic tracking

### 💰 Monetization Dashboard

#### **Opportunity Identification**
The AI continuously analyzes your projects for:
- **SaaS Potential**: APIs that could become services
- **Course Material**: Projects suitable for tutorials
- **Marketplace Items**: Reusable components or templates
- **Consulting Opportunities**: Expertise demonstration
- **Open Source Sponsorship**: Popular project monetization

#### **Revenue Tracking**
- Monthly revenue summaries
- Project-specific profitability
- Time investment vs. return analysis
- Growth trend visualization

#### **Freelance Job Matching**
- Skills-based job recommendations
- Rate comparison and negotiation tips
- Application template generation
- Project portfolio optimization

## 🛠️ Advanced Features

### 🔧 Custom AI Rules

You can customize how AI agents work on your projects by editing the `rules.md` file:

```markdown
# Custom Project Rules

## Code Style
- Use TypeScript for all new React components
- Prefer functional components over class components
- Always include proper error handling

## Documentation
- Every API endpoint must have OpenAPI documentation
- Include usage examples in all README files
- Maintain changelog for version tracking

## Testing
- Minimum 80% code coverage required
- Include both unit and integration tests
- Use Jest for JavaScript testing
```

### 🚀 Deployment Automation

#### **Local Development**
```bash
# Start development environment
./scripts/deploy.sh

# View logs
./scripts/deploy.sh logs

# Stop all services
./scripts/deploy.sh stop
```

#### **Production Deployment**
```bash
# Deploy to production
./scripts/deploy.sh deploy --env=production

# Update existing deployment
./scripts/deploy.sh update

# Rollback to previous version
./scripts/deploy.sh rollback
```

#### **Port Management**
Zenith Coder automatically manages ports to prevent conflicts:
- **Frontend**: Port 3000 (configurable)
- **Backend**: Port 8000 (configurable)
- **Database**: Port 5432 (internal)
- **Redis**: Port 6379 (internal)
- **Traefik**: Port 80/443 (HTTP/HTTPS)

### 🔒 Security & Privacy

#### **API Key Management**
- All API keys are encrypted at rest
- Keys are never logged or exposed
- Automatic key rotation support
- Usage monitoring and alerts

#### **Data Privacy**
- All project data stays on your machine
- No code is sent to external services without consent
- AI interactions are logged locally only
- Optional telemetry can be disabled

## 🎯 Workflows for Different Scenarios

### 🌅 **Morning Routine**
1. Open Zenith Coder dashboard
2. Review overnight AI analysis
3. Check prioritized task list
4. Start with a quick win task
5. Begin first Pomodoro session

### 🔥 **High Energy Sessions**
1. Tackle complex coding tasks
2. Work on new feature development
3. Refactor and optimize code
4. Write comprehensive documentation

### 🌙 **Low Energy Sessions**
1. Focus on quick wins
2. Update documentation
3. Review and merge pull requests
4. Plan future tasks with AI assistance

### 💰 **Monetization Focus**
1. Review monetization opportunities
2. Research market demand
3. Create marketing materials
4. Apply to relevant freelance jobs
5. Update project portfolios

## 🆘 Troubleshooting

### Common Issues

#### **AI Assistant Not Responding**
1. Check API key configuration in `.env`
2. Verify internet connection
3. Check API service status
4. Try switching to a different AI model

#### **Projects Not Scanning**
1. Ensure proper file permissions
2. Check if directories exist
3. Verify Git repository status
4. Review scan configuration settings

#### **Dashboard Not Loading**
1. Check if all Docker containers are running
2. Verify port availability
3. Check browser console for errors
4. Restart services with `./scripts/deploy.sh restart`

#### **Performance Issues**
1. Check available system resources
2. Optimize Docker container limits
3. Clear browser cache
4. Review database performance

### Getting Help

- **Documentation**: Check `/docs` directory for detailed guides
- **Logs**: Use `./scripts/deploy.sh logs` to view system logs
- **Health Check**: Visit `/health` endpoint for system status
- **Community**: Join our Discord for community support

## 🚀 Tips for Maximum Productivity

### 🧠 **ADHD-Specific Strategies**
1. **Start Small**: Always begin with quick wins
2. **Time Box Everything**: Use the Pomodoro timer religiously
3. **Visual Progress**: Keep the dashboard open for motivation
4. **Reduce Decisions**: Let AI suggest next tasks
5. **Celebrate Wins**: Acknowledge completed tasks

### 💡 **Vibecoding Best Practices**
1. **Trust the AI**: Let it handle routine documentation
2. **Focus on Value**: Prioritize monetizable features
3. **Maintain Momentum**: Switch between projects when stuck
4. **Document Everything**: Future you (and AI) will thank you
5. **Think Business**: Always consider monetization potential

### 🎯 **Goal Achievement**
1. **Set Clear Objectives**: Define what "top vibecoder" means to you
2. **Track Progress**: Use the dashboard metrics
3. **Iterate Quickly**: Deploy early, improve continuously
4. **Learn Constantly**: Stay updated with AI industry trends
5. **Network Actively**: Use freelance opportunities to build connections

## 🔮 What's Next?

Zenith Coder is continuously evolving. Upcoming features include:

- **Voice Interface**: Talk to your AI assistant
- **Mobile App**: Manage projects on the go
- **Team Collaboration**: Share projects with team members
- **Advanced Analytics**: Deeper insights into your development patterns
- **Custom AI Models**: Train models on your specific coding style
- **Integration Hub**: Connect with more tools and services

---

Welcome to the future of development productivity. With Zenith Coder as your companion, you're well on your way to becoming the top vibecoder you aspire to be! 🚀

