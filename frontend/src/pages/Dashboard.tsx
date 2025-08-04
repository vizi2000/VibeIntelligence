import { useQuery } from '@tanstack/react-query';
import { 
  Sparkles, 
  TrendingUp, 
  Target, 
  Heart,
  Zap,
  AlertTriangle,
  CheckCircle,
  Coffee,
  Lightbulb
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { projectsApi, statsApi, aiApi } from '@/services/api';
import { useState, useEffect } from 'react';
import toast from 'react-hot-toast';

export default function Dashboard() {
  const [greeting, setGreeting] = useState('');
  const [quantumIdea, setQuantumIdea] = useState<string>('');

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getProjects,
  });

  const { data: stats } = useQuery({
    queryKey: ['usage-stats'],
    queryFn: statsApi.getUsageStats,
  });

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) {
      setGreeting('Good morning, Vibecoder! ☀️');
    } else if (hour < 17) {
      setGreeting('Good afternoon, keep the vibe flowing! 🌤️');
    } else {
      setGreeting('Good evening, time to wind down! 🌙');
    }
  }, []);

  const handleGetQuantumIdea = async () => {
    try {
      const idea = await aiApi.getQuantumIdea();
      setQuantumIdea(idea.idea);
      toast.success('Quantum idea generated! 🎨');
    } catch (error) {
      toast.error('Failed to generate quantum idea');
    }
  };

  const activeProjects = projects?.filter(p => p.status === 'active') || [];
  const healthyProjects = activeProjects.filter(p => p.health_score > 80).length;
  const needsAttention = activeProjects.filter(p => p.health_score < 60).length;

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <Card className="bg-gradient-to-r from-purple-500 via-pink-500 to-rose-500 text-white border-0">
        <CardContent className="p-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{greeting}</h1>
              <p className="text-lg opacity-90 mb-4">
                Your vibe level is {stats?.vibe_level || 'high'} today! Let's create something amazing.
              </p>
              <div className="flex gap-3">
                <Button 
                  variant="secondary" 
                  className="bg-white/20 hover:bg-white/30 text-white border-white/30"
                  onClick={handleGetQuantumIdea}
                >
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Get Quantum Idea
                </Button>
                <Button variant="secondary" className="bg-white/20 hover:bg-white/30 text-white border-white/30">
                  <Coffee className="w-4 h-4 mr-2" />
                  Start Focus Session
                </Button>
              </div>
            </div>
            <div className="text-6xl">
              <Sparkles className="w-24 h-24 opacity-50" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Quantum Idea Display */}
      {quantumIdea && (
        <Card className="border-purple-500/50 bg-purple-50/50 dark:bg-purple-950/20">
          <CardContent className="p-6">
            <div className="flex items-start gap-3">
              <Sparkles className="w-6 h-6 text-purple-600 mt-1" />
              <div>
                <h3 className="font-semibold mb-2">Quantum Idea</h3>
                <p className="text-muted-foreground">{quantumIdea}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Projects
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeProjects.length}</div>
            <p className="text-xs text-muted-foreground mt-1">
              {healthyProjects} healthy, {needsAttention} need attention
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Eco Score
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {stats?.eco_score || 95}%
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Sustainable coding! 🌱
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              AI Tokens Used
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {stats?.total_tokens?.toLocaleString() || '0'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Cost: ${stats?.total_cost?.toFixed(2) || '0.00'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Vibe Level
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold flex items-center gap-2">
              {stats?.vibe_level || 'High'}
              <Heart className="w-5 h-5 text-pink-500" />
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Keep spreading joy! ✨
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Projects Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Active Projects</CardTitle>
              <CardDescription>
                Your projects with AI-powered insights
              </CardDescription>
            </CardHeader>
            <CardContent>
              {projectsLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Loading projects...
                </div>
              ) : activeProjects.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No active projects yet. Create one to get started!
                </div>
              ) : (
                <div className="space-y-4">
                  {activeProjects.slice(0, 5).map((project) => (
                    <div
                      key={project.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors"
                    >
                      <div className="flex items-center gap-4">
                        <div className={`w-3 h-3 rounded-full ${
                          project.health_score > 80 ? 'bg-green-500' :
                          project.health_score > 60 ? 'bg-yellow-500' : 'bg-red-500'
                        }`} />
                        <div>
                          <h4 className="font-semibold">{project.name}</h4>
                          <p className="text-sm text-muted-foreground">
                            {project.description}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-right">
                          <div className="text-sm font-medium">
                            Health: {project.health_score}%
                          </div>
                          <div className="text-xs text-muted-foreground">
                            Last scan: {new Date(project.last_scan).toLocaleDateString()}
                          </div>
                        </div>
                        <Button size="sm" variant="outline">
                          View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="w-5 h-5" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full justify-start" variant="outline">
                <Target className="w-4 h-4 mr-2" />
                Scan All Projects
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <TrendingUp className="w-4 h-4 mr-2" />
                Generate Weekly Report
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <CheckCircle className="w-4 h-4 mr-2" />
                Fix All DEI Issues
              </Button>
              <Button className="w-full justify-start" variant="outline">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Security Audit
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Heart className="w-5 h-5 text-pink-500" />
                Wellness Check
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between">
                  <span>Coding time today</span>
                  <span className="font-medium">2h 45m</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Breaks taken</span>
                  <span className="font-medium text-green-600">3</span>
                </div>
                <div className="flex items-center justify-between">
                  <span>Hydration reminder</span>
                  <span className="font-medium text-blue-600">In 15m</span>
                </div>
              </div>
              <Button className="w-full mt-4" variant="secondary">
                <Coffee className="w-4 h-4 mr-2" />
                Take a Break
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}