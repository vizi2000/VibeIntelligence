import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Textarea } from '@/components/ui/textarea.jsx'
import { 
  Search, 
  Bell, 
  User, 
  BarChart3, 
  FolderOpen, 
  CheckSquare, 
  Bot, 
  DollarSign, 
  Rocket, 
  BookOpen, 
  Settings,
  Plus,
  Star,
  AlertTriangle,
  CheckCircle,
  Clock,
  Target,
  TrendingUp,
  Github,
  ExternalLink,
  MessageCircle,
  Zap,
  Coffee,
  Award,
  Lightbulb
} from 'lucide-react'
import './App.css'

// Mock data for the dashboard
const mockProjects = [
  {
    id: 1,
    name: "Zenith Coder",
    description: "AI-powered development platform",
    status: "active",
    priority: "high",
    healthScore: 92,
    docsProgress: 85,
    issues: 3,
    revenue: 0,
    tags: ["Python", "FastAPI", "React", "AI", "MVP-Ready"],
    lastCommit: "2 hours ago",
    nextTask: "Deploy MVP"
  },
  {
    id: 2,
    name: "E-commerce API",
    description: "RESTful API for online stores",
    status: "active",
    priority: "high",
    healthScore: 76,
    docsProgress: 45,
    issues: 7,
    revenue: 1200,
    tags: ["Node.js", "Express", "MongoDB", "Stripe", "Production"],
    lastCommit: "5 days ago",
    nextTask: "Security audit"
  },
  {
    id: 3,
    name: "Personal Website",
    description: "Portfolio and blog website",
    status: "maintenance",
    priority: "low",
    healthScore: 58,
    docsProgress: 20,
    issues: 12,
    revenue: 0,
    tags: ["React", "Gatsby", "GraphQL", "Netlify"],
    lastCommit: "2 weeks ago",
    nextTask: "Update README"
  }
]

const mockTasks = [
  { id: 1, title: "Update README for API project", duration: 15, priority: "high", type: "documentation" },
  { id: 2, title: "Fix authentication bug", duration: 30, priority: "medium", type: "bug" },
  { id: 3, title: "Review PR #23", duration: 20, priority: "low", type: "review" }
]

const mockQuickWins = [
  "Add license to 2 projects",
  "Fix broken links in docs", 
  "Update dependencies"
]

const mockOpportunities = [
  { title: "E-commerce API → SaaS", potential: "$500/mo" },
  { title: "Tutorial series → Course", potential: "$1,200" },
  { title: "Code templates → Marketplace", potential: "TBD" }
]

const mockFreelanceJobs = [
  { title: "Python API development", rate: "$75/hr", type: "hourly" },
  { title: "React dashboard", rate: "$2,500", type: "fixed" }
]

const mockAINews = [
  "New Claude 3.5 features",
  "AI coding assistants comparison", 
  "Monetizing GitHub projects"
]

function App() {
  const [activeView, setActiveView] = useState('dashboard')
  const [aiMessage, setAiMessage] = useState('')
  const [currentTime, setCurrentTime] = useState(new Date())

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  const getGreeting = () => {
    const hour = currentTime.getHours()
    if (hour < 12) return "Good morning"
    if (hour < 17) return "Good afternoon"
    return "Good evening"
  }

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'default'
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'maintenance': return 'bg-yellow-500'
      case 'archived': return 'bg-gray-500'
      default: return 'bg-blue-500'
    }
  }

  const renderDashboard = () => (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{getGreeting()}, Vibecoder! 🌅</h1>
              <p className="text-lg opacity-90 mb-4">You have 3 quick wins ready to boost your momentum</p>
              <div className="flex gap-3">
                <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
                  <Target className="w-4 h-4 mr-2" />
                  Start Focus Session
                </Button>
                <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
                  <Bot className="w-4 h-4 mr-2" />
                  Ask AI Assistant
                </Button>
                <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
                  <Lightbulb className="w-4 h-4 mr-2" />
                  View Suggestions
                </Button>
              </div>
            </div>
            <div className="text-6xl opacity-50">🚀</div>
          </div>
        </CardContent>
      </Card>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Column 1: Active Projects */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FolderOpen className="w-5 h-5" />
                Active Projects ({mockProjects.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {mockProjects.map((project) => (
                <div key={project.id} className="border rounded-lg p-4 space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <div className={`w-3 h-3 rounded-full ${getStatusColor(project.status)}`} />
                      <h3 className="font-semibold">{project.name}</h3>
                    </div>
                    {project.priority === 'high' && (
                      <Badge variant="destructive" className="text-xs">
                        <Star className="w-3 h-3 mr-1" />
                        High Priority
                      </Badge>
                    )}
                  </div>
                  
                  <div className="space-y-2 text-sm text-muted-foreground">
                    <div className="flex items-center gap-2">
                      <span>📝 Documentation:</span>
                      <Progress value={project.docsProgress} className="flex-1 h-2" />
                      <span>{project.docsProgress}%</span>
                    </div>
                    <div>🐛 {project.issues} open issues</div>
                    <div>🚀 {project.nextTask}</div>
                  </div>
                  
                  <div className="flex flex-wrap gap-1">
                    {project.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {project.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{project.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>
              ))}
              
              <Button variant="outline" className="w-full">
                <Plus className="w-4 h-4 mr-2" />
                Add New Project
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Column 2: AI Assistant & Tasks */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="w-5 h-5" />
                AI Assistant
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="bg-muted/50 rounded-lg p-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white text-sm">
                    🤖
                  </div>
                  <div className="flex-1 space-y-2">
                    <p className="text-sm">
                      "I noticed you haven't committed to the Zenith Coder repo in 2 days. 
                      Would you like me to help you create a quick documentation update?"
                    </p>
                    <div className="flex gap-2">
                      <Button size="sm" variant="default">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Yes, help me
                      </Button>
                      <Button size="sm" variant="outline">
                        <Clock className="w-3 h-3 mr-1" />
                        Remind me later
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <CheckSquare className="w-4 h-4" />
                  Today's Focus Tasks
                </h4>
                <div className="space-y-2">
                  {mockTasks.map((task) => (
                    <div key={task.id} className="flex items-center gap-3 p-2 rounded border">
                      <div className="text-xs bg-muted px-2 py-1 rounded">
                        ⏰ {task.duration} min
                      </div>
                      <div className={`w-3 h-3 rounded-full ${
                        task.priority === 'high' ? 'bg-red-500' : 
                        task.priority === 'medium' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <span className="text-sm flex-1">{task.title}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Zap className="w-4 h-4" />
                  Quick Wins Available ({mockQuickWins.length})
                </h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {mockQuickWins.map((win, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-green-500 rounded-full" />
                      {win}
                    </li>
                  ))}
                </ul>
              </div>
              
              <Button className="w-full">
                <Coffee className="w-4 h-4 mr-2" />
                Start Pomodoro Session
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Column 3: Insights & Monetization */}
        <div className="lg:col-span-1 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="w-5 h-5" />
                Monetization Insights
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">$2,400</div>
                  <div className="text-xs text-muted-foreground">This Month</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">47</div>
                  <div className="text-xs text-muted-foreground">Tasks Done</div>
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Target className="w-4 h-4" />
                  Opportunities
                </h4>
                <div className="space-y-2">
                  {mockOpportunities.map((opp, index) => (
                    <div key={index} className="flex justify-between items-center text-sm">
                      <span>{opp.title}</span>
                      <Badge variant="outline">{opp.potential}</Badge>
                    </div>
                  ))}
                </div>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Trending in AI
                </h4>
                <ul className="space-y-1 text-sm text-muted-foreground">
                  {mockAINews.map((news, index) => (
                    <li key={index} className="flex items-center gap-2">
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
                      "{news}"
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="border-t pt-4">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Award className="w-4 h-4" />
                  Freelance Matches ({mockFreelanceJobs.length} new)
                </h4>
                <div className="space-y-2">
                  {mockFreelanceJobs.map((job, index) => (
                    <div key={index} className="p-2 border rounded text-sm">
                      <div className="font-medium">{job.title}</div>
                      <div className="text-muted-foreground">{job.rate} {job.type}</div>
                    </div>
                  ))}
                </div>
              </div>
              
              <Button variant="outline" className="w-full">
                <ExternalLink className="w-4 h-4 mr-2" />
                View All Opportunities
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )

  const renderAIAssistant = () => (
    <div className="max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bot className="w-6 h-6" />
            Zenith AI Assistant
          </CardTitle>
          <CardDescription>
            Your intelligent development companion powered by multiple AI models
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* AI Conversation */}
          <div className="space-y-4 max-h-96 overflow-y-auto">
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white text-sm">
                🤖
              </div>
              <div className="flex-1 bg-muted/50 rounded-lg p-4">
                <p className="text-sm mb-3">
                  Good morning! I've analyzed your projects overnight and found some opportunities to improve your development workflow.
                </p>
                <p className="text-sm mb-3">Here's what I discovered:</p>
                <ul className="text-sm space-y-1 mb-4">
                  <li>• 3 projects are missing proper documentation</li>
                  <li>• Your E-commerce API has security vulnerabilities</li>
                  <li>• There are 2 freelance projects that match your skills</li>
                </ul>
                <p className="text-sm mb-4">Which would you like to tackle first?</p>
                <div className="flex gap-2 flex-wrap">
                  <Button size="sm" variant="default">
                    <BookOpen className="w-3 h-3 mr-1" />
                    Fix Documentation
                  </Button>
                  <Button size="sm" variant="outline">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Security Audit
                  </Button>
                  <Button size="sm" variant="outline">
                    <ExternalLink className="w-3 h-3 mr-1" />
                    View Freelance
                  </Button>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-sm">
                👤
              </div>
              <div className="flex-1 bg-blue-50 rounded-lg p-4">
                <p className="text-sm">Help me create documentation for the E-commerce API</p>
              </div>
            </div>
            
            <div className="flex gap-3">
              <div className="w-8 h-8 bg-indigo-500 rounded-full flex items-center justify-center text-white text-sm">
                🤖
              </div>
              <div className="flex-1 bg-muted/50 rounded-lg p-4">
                <p className="text-sm mb-3">Perfect choice! I'll help you create comprehensive docs.</p>
                <p className="text-sm mb-3">I've analyzed your API code and found:</p>
                <ul className="text-sm space-y-1 mb-4">
                  <li>• 12 endpoints that need documentation</li>
                  <li>• 3 data models to document</li>
                  <li>• Authentication flow to explain</li>
                </ul>
                <p className="text-sm mb-3">I can generate:</p>
                <ul className="text-sm space-y-1 mb-4">
                  <li>✅ OpenAPI/Swagger specification</li>
                  <li>✅ README with setup instructions</li>
                  <li>✅ API usage examples</li>
                  <li>✅ Authentication guide</li>
                </ul>
                <p className="text-sm mb-4">This will take about 5 minutes. Shall I proceed?</p>
                <div className="flex gap-2">
                  <Button size="sm" variant="default">
                    <Rocket className="w-3 h-3 mr-1" />
                    Generate Docs
                  </Button>
                  <Button size="sm" variant="outline">
                    <Settings className="w-3 h-3 mr-1" />
                    Customize
                  </Button>
                  <Button size="sm" variant="outline">
                    <CheckSquare className="w-3 h-3 mr-1" />
                    Show Preview
                  </Button>
                </div>
              </div>
            </div>
          </div>
          
          {/* Input Area */}
          <div className="border-t pt-4">
            <div className="flex gap-2">
              <Textarea 
                placeholder="Type your message here..."
                value={aiMessage}
                onChange={(e) => setAiMessage(e.target.value)}
                className="flex-1 min-h-[60px]"
              />
              <div className="flex flex-col gap-2">
                <Button size="sm" variant="outline">
                  🎤
                </Button>
                <Button size="sm" variant="outline">
                  📎
                </Button>
                <Button size="sm" disabled={!aiMessage.trim()}>
                  <Rocket className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
                Z
              </div>
              <h1 className="text-xl font-bold">Zenith Coder</h1>
            </div>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
              <Input placeholder="Search projects..." className="pl-10 w-64" />
            </div>
            <Button variant="ghost" size="sm">
              <Bell className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm">
              <User className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className="w-72 border-r bg-card/50 min-h-screen p-4">
          <nav className="space-y-2">
            {[
              { id: 'dashboard', label: 'Dashboard', icon: BarChart3 },
              { id: 'projects', label: 'Projects', icon: FolderOpen },
              { id: 'tasks', label: 'Tasks', icon: CheckSquare },
              { id: 'ai-assistant', label: 'AI Assistant', icon: Bot },
              { id: 'monetization', label: 'Monetization', icon: DollarSign },
              { id: 'deployment', label: 'Deployment', icon: Rocket },
              { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
              { id: 'settings', label: 'Settings', icon: Settings }
            ].map((item) => (
              <Button
                key={item.id}
                variant={activeView === item.id ? "default" : "ghost"}
                className="w-full justify-start"
                onClick={() => setActiveView(item.id)}
              >
                <item.icon className="w-4 h-4 mr-2" />
                {item.label}
              </Button>
            ))}
          </nav>
          
          <div className="mt-8 p-4 bg-muted/50 rounded-lg">
            <h3 className="font-semibold mb-2 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" />
              Quick Stats
            </h3>
            <div className="space-y-2 text-sm">
              <div>• 12 Active Projects</div>
              <div>• 8 Tasks Today</div>
              <div>• $2.4k This Month</div>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeView === 'dashboard' && renderDashboard()}
          {activeView === 'ai-assistant' && renderAIAssistant()}
          {activeView !== 'dashboard' && activeView !== 'ai-assistant' && (
            <div className="flex items-center justify-center h-64">
              <div className="text-center">
                <div className="text-4xl mb-4">🚧</div>
                <h2 className="text-xl font-semibold mb-2">Coming Soon</h2>
                <p className="text-muted-foreground">
                  The {activeView.replace('-', ' ')} section is under development
                </p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  )
}

export default App

