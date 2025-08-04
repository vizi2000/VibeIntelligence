import { useState } from 'react';
import { 
  TrendingUp, 
  Bot,
  CheckCircle,
  Clock,
  MoreVertical
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface Project {
  id: string;
  name: string;
  status: 'in-progress' | 'on-hold' | 'completed';
  progress: number;
  health: 'good' | 'fair' | 'poor';
  inProgress: number;
  notStarted: number;
  completed: number;
  approved?: number;
}

export default function Dashboard() {
  const [projects] = useState<Project[]>([
    {
      id: '1',
      name: 'Authentication System',
      status: 'in-progress',
      progress: 53,
      health: 'good',
      inProgress: 1,
      notStarted: 1,
      completed: 0,
    },
    {
      id: '2',
      name: 'API Development',
      status: 'on-hold',
      progress: 50,
      health: 'fair',
      inProgress: 0,
      notStarted: 0,
      completed: 1,
    },
    {
      id: '3',
      name: 'Machine Learning Model',
      status: 'completed',
      progress: 83,
      health: 'good',
      completed: 0,
      approved: 1,
      inProgress: 0,
      notStarted: 0,
    },
  ]);

  const [revenue] = useState(4250);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'in-progress':
        return 'text-blue-600';
      case 'on-hold':
        return 'text-yellow-600';
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

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Active Projects</h1>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-12 gap-6">
        {/* Projects Section - Left Side */}
        <div className="col-span-8 space-y-4">
          {projects.map((project) => (
            <Card key={project.id} className="overflow-hidden card-hover">
              <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{project.name}</h3>
                    <div className="flex items-center gap-4 mt-2">
                      <span className={getHealthBadge(project.health)}>
                        {project.health.charAt(0).toUpperCase() + project.health.slice(1)}
                      </span>
                      <span className={`text-sm font-medium ${getStatusColor(project.status)}`}>
                        {project.status === 'in-progress' ? 'In Progress' : 
                         project.status === 'on-hold' ? 'On Hold' : 'Completed'}
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
                    <span className="text-gray-600">{project.progress}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${project.progress}%` }}
                    />
                  </div>
                </div>

                {/* Status Pills */}
                <div className="flex items-center gap-4 text-sm">
                  {project.inProgress > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-blue-500 rounded-full" />
                      <span className="text-gray-600">In Progress</span>
                    </div>
                  )}
                  {project.notStarted && project.notStarted > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-gray-400 rounded-full" />
                      <span className="text-gray-600">On not</span>
                    </div>
                  )}
                  {project.completed > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-green-500 rounded-full" />
                      <span className="text-gray-600">Completed</span>
                    </div>
                  )}
                  {project.approved && project.approved > 0 && (
                    <div className="flex items-center gap-1">
                      <span className="w-2 h-2 bg-purple-500 rounded-full" />
                      <span className="text-gray-600">Approved</span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
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
                  <p className="text-sm">Sure! Here are some suggestions...</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Monetization Card */}
          <Card className="overflow-hidden">
            <CardHeader className="pb-3">
              <CardTitle className="text-lg">Monetization</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Revenue */}
              <div>
                <p className="text-sm text-gray-600">Revenue</p>
                <p className="text-3xl font-bold gradient-text">${revenue.toLocaleString()}</p>
                <div className="flex items-center gap-2 mt-1">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-sm text-green-600">+12% from last month</span>
                </div>
              </div>

              {/* Opportunities */}
              <div className="pt-4 border-t">
                <p className="text-sm text-gray-600 mb-3">Freelance Opportunities</p>
                <div className="space-y-2">
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <span className="text-sm">Payment Integration</span>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <span className="text-sm">Code Review</span>
                    <CheckCircle className="w-4 h-4 text-green-500" />
                  </div>
                  <div className="flex items-center justify-between p-2 bg-gray-50 rounded-lg">
                    <span className="text-sm">Bug Fixes</span>
                    <Clock className="w-4 h-4 text-yellow-500" />
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}