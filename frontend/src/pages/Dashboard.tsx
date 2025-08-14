import { useQuery } from '@tanstack/react-query';
import { 
  TrendingUp, 
  Bot,
  CheckCircle,
  Clock,
  MoreVertical,
  Activity,
  AlertTriangle
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { projectsApi, api } from '@/services/api';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const navigate = useNavigate();
  
  // Fetch real projects
  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getProjects,
  });

  // Fetch agent tasks for activity tracking
  const { data: agentTasks } = useQuery({
    queryKey: ['agent-tasks'],
    queryFn: async () => {
      const response = await api.get('/agents/tasks');
      return response.data;
    },
  });

  // Fetch system stats
  const { data: systemStats } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const response = await api.get('/agents/stats');
      return response.data;
    },
  });

  // Calculate revenue from agent tasks (mock calculation)
  const revenue = agentTasks?.reduce((acc: number, task: any) => {
    if (task.status === 'completed') {
      return acc + (task.task_type === 'monetization' ? 250 : 100);
    }
    return acc;
  }, 0) || 0;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'active':
        return 'text-blue-600';
      case 'maintenance':
        return 'text-yellow-600';
      case 'archived':
        return 'text-gray-600';
      default:
        return 'text-gray-600';
    }
  };

  const getHealthBadge = (health: string) => {
    const colors = {
      good: 'bg-green-100 text-green-800',
      fair: 'bg-yellow-100 text-yellow-800',
      poor: 'bg-red-100 text-red-800',
    };
    return `inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colors[health as keyof typeof colors]}`;
  };

  const getHealthIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    return <AlertTriangle className="w-5 h-5 text-red-600" />;
  };

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600 mt-1">Overview of your projects and agent activity</p>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Projects Section - Left Side */}
        <div className="col-span-8 space-y-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Active Projects</h2>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => navigate('/projects')}
            >
              View All
            </Button>
          </div>

          {projectsLoading ? (
            <Card className="p-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
                <div className="h-2 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-2 bg-gray-200 rounded w-1/2"></div>
              </div>
            </Card>
          ) : projects && Array.isArray(projects) && projects.length > 0 ? (
            projects.slice(0, 5).map((project: any) => (
              <Card key={project.id} className="overflow-hidden card-hover">
                <CardContent className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                        {getHealthIcon(project.health_score)}
                      </div>
                      <div className="flex items-center gap-4 mt-2">
                        <span className={getHealthBadge(project.health_score >= 80 ? 'good' : project.health_score >= 60 ? 'fair' : 'poor')}>
                          Health: {project.health_score}%
                        </span>
                        <span className={`text-sm font-medium ${getStatusColor(project.status || 'active')}`}>
                          {project.status || 'Active'}
                        </span>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-600">Health Score</span>
                      <span className="text-gray-900">{project.health_score}%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                        style={{ width: `${project.health_score}%` }}
                      />
                    </div>
                  </div>

                  {/* Project Info */}
                  <div className="flex items-center gap-4 text-sm">
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600">Type:</span>
                      <span className="text-gray-900">{project.project_type || 'Unknown'}</span>
                    </div>
                    {project.is_git_repo && (
                      <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full" />
                        <span className="text-gray-600">Git Repo</span>
                      </div>
                    )}
                    {project.has_documentation && (
                      <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-blue-500 rounded-full" />
                        <span className="text-gray-600">Documented</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))
          ) : (
            <Card className="text-center p-8">
              <h3 className="text-lg font-semibold mb-2">No projects found</h3>
              <p className="text-gray-600 mb-4">Start by scanning your projects directory</p>
              <Button onClick={() => navigate('/projects')}>
                <Activity className="w-4 h-4 mr-2" />
                Go to Projects
              </Button>
            </Card>
          )}
        </div>

        {/* Right Side Panels */}
        <div className="col-span-4 space-y-6">
          {/* AI Assistant Card */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">AI Assistant</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Bot Avatar */}
              <div className="flex justify-center">
                <div className="w-24 h-24 rounded-full gradient-primary flex items-center justify-center">
                  <Bot className="w-12 h-12 text-white" />
                </div>
              </div>
              
              {/* Chat Messages */}
              <div className="space-y-3">
                <div className="chat-bubble chat-bubble-bot">
                  <p className="text-sm">Hello! How can I assist you today?</p>
                </div>
                <div className="chat-bubble chat-bubble-user">
                  <p className="text-sm">Can you suggest some code improvements?</p>
                </div>
                <div className="chat-bubble chat-bubble-bot">
                  <p className="text-sm">I'd be happy to help! Go to the AI Assistant page for a full conversation.</p>
                </div>
              </div>

              <Button 
                className="w-full" 
                onClick={() => navigate('/ai-assistant')}
              >
                Open AI Assistant
              </Button>
            </CardContent>
          </Card>

          {/* Monetization Card */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Agent Activity</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Revenue */}
              <div>
                <p className="text-sm text-gray-600">AI Task Revenue</p>
                <p className="text-3xl font-bold gradient-text">${revenue.toLocaleString()}</p>
                <div className="flex items-center gap-2 mt-1">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-600">
                    From {agentTasks?.filter((t: any) => t.status === 'completed').length || 0} completed tasks
                  </span>
                </div>
              </div>

              {/* Agent Activity */}
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600 mb-3">Recent Agent Tasks</p>
                <div className="space-y-2">
                  {Array.isArray(agentTasks) && agentTasks.slice(0, 3).map((task: any, index: number) => (
                    <div key={task.id || index} className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                      <span className="text-sm truncate">{task.task_type}</span>
                      {task.status === 'completed' ? (
                        <CheckCircle className="w-4 h-4 text-green-500" />
                      ) : task.status === 'running' ? (
                        <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />
                      ) : (
                        <Clock className="w-4 h-4 text-gray-400" />
                      )}
                    </div>
                  )) || (
                    <div className="text-sm text-gray-500">No recent activity</div>
                  )}
                </div>
              </div>

              {/* System Stats */}
              {systemStats && (
                <div className="pt-4 border-t">
                  <p className="text-sm text-gray-600 mb-3">System Performance</p>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Active Agents</span>
                      <span className="font-medium">{systemStats.active_agents || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total Tasks</span>
                      <span className="font-medium">{systemStats.total_tasks || 0}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Success Rate</span>
                      <span className="font-medium text-green-600">
                        {systemStats.success_rate || 0}%
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}