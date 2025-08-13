import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useState } from 'react';
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
import { api } from '@/services/api';
import toast from 'react-hot-toast';

export default function Projects() {
  const queryClient = useQueryClient();
  const [scanStatus, setScanStatus] = useState<{ id?: string; status?: string; message?: string }>({});
  const [lastScanResult, setLastScanResult] = useState<any>(null);
  
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: projectsApi.getProjects,
  });

  const scanProject = (path: string) => {
    scanProjectMutation.mutate(path);
  };

  const deployProject = async (projectId: string, projectName: string) => {
    try {
      const response = await api.post('/deploy/deploy', {
        project_id: projectId,
        environment: 'staging',
        deployment_type: 'docker'
      });
      
      if (response.data.deployment_id) {
        toast.success(`Deployment started for ${projectName}`);
        
        // Poll for status
        const pollInterval = setInterval(async () => {
          try {
            const statusResponse = await api.get(`/deploy/status/${response.data.deployment_id}`);
            const status = statusResponse.data;
            
            if (status.message) {
              // Update toast with current status
              toast.loading(status.message, { id: 'deploy-status' });
            }
            
            if (status.status === 'success') {
              clearInterval(pollInterval);
              toast.dismiss('deploy-status');
              toast.success('Deployment successful! 🚀', { duration: 5000 });
              
              if (status.deployment_url) {
                toast.success(`Live at: ${status.deployment_url}`, { duration: 10000 });
              }
            } else if (status.status === 'failed') {
              clearInterval(pollInterval);
              toast.dismiss('deploy-status');
              toast.error('Deployment failed: ' + status.error);
            }
          } catch (error) {
            clearInterval(pollInterval);
            toast.dismiss('deploy-status');
          }
        }, 2000);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to start deployment');
    }
  };

  const generateDocs = async (projectId: string, projectName: string) => {
    try {
      const response = await api.post('/documentation/generate', {
        project_id: projectId,
        doc_type: 'readme'
      });
      
      if (response.data.task_id) {
        toast.success(`Documentation generation started for ${projectName}`);
        
        // Poll for status
        const pollInterval = setInterval(async () => {
          try {
            const statusResponse = await api.get(`/documentation/status/${response.data.task_id}`);
            const status = statusResponse.data;
            
            if (status.status === 'completed') {
              clearInterval(pollInterval);
              toast.success('Documentation generated successfully!', { duration: 5000 });
              
              // Show result if available
              if (status.result && status.result.documentation) {
                console.log('Documentation:', status.result.documentation);
              }
            } else if (status.status === 'failed') {
              clearInterval(pollInterval);
              toast.error('Documentation generation failed: ' + status.error);
            }
          } catch (error) {
            clearInterval(pollInterval);
          }
        }, 2000);
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Failed to generate documentation');
    }
  };

  const scanProjectMutation = useMutation({
    mutationFn: async (path: string) => {
      const response = await api.post('/scanner/scan', { path, full_scan: false });
      return response.data;
    },
    onSuccess: (data) => {
      setScanStatus(data);
      toast.success('Project scan started!');
      
      // Poll for scan status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await api.get(`/scanner/scan/${data.scan_id}`);
          const status = statusResponse.data;
          
          setScanStatus(status);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            
            // Get scan details
            if (status.result && status.result.projects_found !== undefined) {
              const result = status.result;
              setLastScanResult(result);
              
              const message = `Scan completed! Found ${result.projects_found} projects. ` +
                `Vibe level: ${result.vibe_level}. Eco-score: ${result.eco_score}%`;
              toast.success(message, { duration: 5000 });
            } else {
              toast.success('Scan completed successfully!');
            }
            
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            setScanStatus({});
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            toast.error('Scan failed: ' + status.message);
            setScanStatus({});
          }
        } catch (error) {
          clearInterval(pollInterval);
        }
      }, 2000);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start scan');
    },
  });

  const scanMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/scanner/scan', { full_scan: true });
      return response.data;
    },
    onSuccess: (data) => {
      setScanStatus(data);
      toast.success('Project scan started!');
      
      // Poll for scan status
      const pollInterval = setInterval(async () => {
        try {
          const statusResponse = await api.get(`/scanner/scan/${data.scan_id}`);
          const status = statusResponse.data;
          
          setScanStatus(status);
          
          if (status.status === 'completed') {
            clearInterval(pollInterval);
            
            // Get scan details
            if (status.result && status.result.projects_found !== undefined) {
              const result = status.result;
              setLastScanResult(result);
              
              const message = `Scan completed! Found ${result.projects_found} projects. ` +
                `Vibe level: ${result.vibe_level}. Eco-score: ${result.eco_score}%`;
              toast.success(message, { duration: 5000 });
            } else {
              toast.success('Scan completed successfully!');
            }
            
            queryClient.invalidateQueries({ queryKey: ['projects'] });
            setScanStatus({});
          } else if (status.status === 'failed') {
            clearInterval(pollInterval);
            toast.error('Scan failed: ' + status.message);
            setScanStatus({});
          }
        } catch (error) {
          clearInterval(pollInterval);
        }
      }, 2000);
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to start scan');
    },
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

      {/* Last Scan Result */}
      {lastScanResult && (
        <Card className="mb-6 bg-green-50 border-green-200">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle className="w-5 h-5 text-green-600" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900">Last Scan Results</h3>
                <p className="text-sm text-green-700">
                  Found {lastScanResult.projects_found} projects • 
                  Vibe Level: {lastScanResult.vibe_level} • 
                  Eco-Score: {lastScanResult.eco_score}% • 
                  Scan Time: {lastScanResult.scan_time?.toFixed(1)}s
                </p>
                {lastScanResult.duplicates_found > 0 && (
                  <p className="text-sm text-orange-600 mt-1">
                    ⚠️ Found {lastScanResult.duplicates_found} potential duplicates
                  </p>
                )}
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setLastScanResult(null)}
                className="text-green-600 hover:text-green-700"
              >
                Dismiss
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

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
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => scanProject(project.path)}
                    disabled={scanMutation.isPending || scanStatus.status === 'running'}
                  >
                    <Activity className={`w-4 h-4 mr-1 ${scanStatus.status === 'running' ? 'animate-spin' : ''}`} />
                    Scan
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline" 
                    className="flex-1"
                    onClick={() => generateDocs(project.id, project.name)}
                  >
                    <FileText className="w-4 h-4 mr-1" />
                    Docs
                  </Button>
                  <Button 
                    size="sm" 
                    className="flex-1"
                    onClick={() => deployProject(project.id, project.name)}
                  >
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
            <Button 
              onClick={() => scanMutation.mutate()}
              disabled={scanMutation.isPending || scanStatus.status === 'running'}
            >
              <Activity className={`w-4 h-4 mr-2 ${scanStatus.status === 'running' ? 'animate-spin' : ''}`} />
              {scanStatus.status === 'running' ? 'Scanning...' : 'Start Project Scan'}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}