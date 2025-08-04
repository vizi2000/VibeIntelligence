import { useQuery } from '@tanstack/react-query';
import { 
  FolderOpen, 
  GitBranch, 
  Activity,
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  Zap
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { projectsApi } from '@/services/api';

export default function Projects() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getProjects,
  });

  const getHealthColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="w-5 h-5 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="w-5 h-5 text-yellow-600" />;
    return <AlertTriangle className="w-5 h-5 text-red-600" />;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Loading your projects...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Projects</h1>
        <p className="text-muted-foreground">
          Manage and monitor all your vibecoding projects
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {projects?.map((project) => (
          <Card key={project.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-2">
                  <FolderOpen className="w-5 h-5 text-purple-600" />
                  <CardTitle className="text-lg">{project.name}</CardTitle>
                </div>
                {getHealthIcon(project.health_score)}
              </div>
              <CardDescription className="mt-1">
                {project.description || 'No description available'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Health Score</span>
                  <span className={`font-medium ${getHealthColor(project.health_score)}`}>
                    {project.health_score}%
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Type</span>
                  <span className="font-medium">{project.project_type || 'Unknown'}</span>
                </div>

                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Status</span>
                  <span className={`font-medium capitalize ${
                    project.status === 'active' ? 'text-green-600' : 'text-gray-600'
                  }`}>
                    {project.status}
                  </span>
                </div>

                {project.git_url && (
                  <div className="flex items-center gap-2 text-sm">
                    <GitBranch className="w-4 h-4 text-muted-foreground" />
                    <span className="truncate text-muted-foreground">
                      {project.current_branch || 'main'}
                    </span>
                  </div>
                )}

                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Clock className="w-4 h-4" />
                  <span>
                    Last scan: {project.last_scan 
                      ? new Date(project.last_scan).toLocaleDateString()
                      : 'Never'}
                  </span>
                </div>

                <div className="pt-3 flex gap-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    <Activity className="w-4 h-4 mr-1" />
                    Scan
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    <FileText className="w-4 h-4 mr-1" />
                    Docs
                  </Button>
                  <Button size="sm" className="flex-1">
                    <Zap className="w-4 h-4 mr-1" />
                    Deploy
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {(!projects || projects.length === 0) && (
        <Card className="text-center py-12">
          <CardContent>
            <FolderOpen className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold mb-2">No projects found</h3>
            <p className="text-muted-foreground mb-4">
              Start by scanning your projects directory
            </p>
            <Button>
              <Activity className="w-4 h-4 mr-2" />
              Start Project Scan
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}