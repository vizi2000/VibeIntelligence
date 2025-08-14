import axios from 'axios';
import toast from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.BASE_URL === '/vi/' ? '/vi/api/v1' : '/api/v1');

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      toast.error('Server error. Please try again later.');
    }
    return Promise.reject(error);
  }
);

export interface ProjectAnalysis {
  project_id: string;
  health_score: number;
  issues_count: number;
  documentation_score: number;
  eco_score: number;
  suggestions: string[];
  security_issues: SecurityIssue[];
  dei_issues: DEIIssue[];
}

export interface SecurityIssue {
  severity: 'low' | 'medium' | 'high' | 'critical';
  file: string;
  line: number;
  message: string;
  suggestion: string;
}

export interface DEIIssue {
  term: string;
  suggestion: string;
  file: string;
  line: number;
}

export interface AIGenerateRequest {
  prompt: string;
  task_type?: string;
  temperature?: number;
  max_tokens?: number;
  context?: Record<string, any>;
}

export interface AIGenerateResponse {
  content: string;
  model_used: string;
  tokens_used: number;
  cost: number;
  eco_score: number;
  provider: string;
}

export interface VibeAnalysis {
  text: string;
  vibe_score: number;
  vibe_emoji: string;
  sentiment: string;
  suggestions: string[];
}

export interface EcoAnalysis {
  code: string;
  eco_score: number;
  lines_of_code: number;
  complexity_score: number;
  optimization_suggestions: string[];
  estimated_carbon_impact: number;
}

export interface QuantumIdea {
  idea: string;
  category: string;
  implementation_difficulty: number;
  potential_impact: number;
  resources_needed: string[];
}

export const aiApi = {
  async generateResponse(request: AIGenerateRequest): Promise<AIGenerateResponse> {
    const { data } = await api.post<AIGenerateResponse>('/ai/generate', request);
    return data;
  },

  async analyzeVibe(text: string): Promise<VibeAnalysis> {
    const { data } = await api.post<VibeAnalysis>('/ai/vibe', { text });
    return data;
  },

  async analyzeEcoImpact(code: string): Promise<EcoAnalysis> {
    const { data } = await api.post<EcoAnalysis>('/ai/eco-score', { code });
    return data;
  },

  async getQuantumIdea(): Promise<QuantumIdea> {
    const { data } = await api.get<QuantumIdea>('/ai/quantum-idea');
    return data;
  },

  async summarizeForADHD(text: string): Promise<string> {
    const { data } = await api.post<{ summary: string }>('/ai/adhd-summary', { text });
    return data.summary;
  },

  async analyzeProject(projectPath: string): Promise<ProjectAnalysis> {
    const { data } = await api.post<ProjectAnalysis>('/projects/analyze', { path: projectPath });
    return data;
  },

  async detectDEIIssues(code: string): Promise<DEIIssue[]> {
    const { data } = await api.post<{ issues: DEIIssue[] }>('/ai/dei-check', { code });
    return data.issues;
  },

  async chat(request: { message: string; context?: string }): Promise<{ response: string }> {
    const { data } = await api.post<{ response: string }>('/ai/chat', request);
    return data;
  },
};

export interface Project {
  id: string;
  name: string;
  description: string;
  path: string;
  status: 'active' | 'maintenance' | 'archived';
  health_score: number;
  last_scan: string;
  created_at: string;
  updated_at: string;
  project_type?: string;
  git_url?: string;
  current_branch?: string;
}

export interface ScanResult {
  id: string;
  project_id: string;
  total_files: number;
  issues_found: number;
  documentation_score: number;
  test_coverage: number;
  dependencies_health: number;
  scan_date: string;
  scan_duration: number;
}

export const projectsApi = {
  async getProjects(): Promise<Project[]> {
    const { data } = await api.get<Project[]>('/projects/');
    return data;
  },

  async getProject(id: string): Promise<Project> {
    const { data } = await api.get<Project>(`/projects/${id}`);
    return data;
  },

  async createProject(project: Partial<Project>): Promise<Project> {
    const { data } = await api.post<Project>('/projects', project);
    return data;
  },

  async updateProject(id: string, project: Partial<Project>): Promise<Project> {
    const { data } = await api.put<Project>(`/projects/${id}`, project);
    return data;
  },

  async deleteProject(id: string): Promise<void> {
    await api.delete(`/projects/${id}`);
  },

  async scanProject(projectPath: string): Promise<ScanResult> {
    const { data } = await api.post<ScanResult>('/scanner/scan', { path: projectPath });
    return data;
  },

  async getScanHistory(projectId: string): Promise<ScanResult[]> {
    const { data } = await api.get<ScanResult[]>(`/scanner/history/${projectId}`);
    return data;
  },
};

export interface UsageStats {
  total_tokens: number;
  total_cost: number;
  eco_score: number;
  requests_count: number;
  average_response_time: number;
  vibe_level: string;
}

export const statsApi = {
  async getUsageStats(): Promise<UsageStats> {
    const { data } = await api.get<UsageStats>('/ai/stats');
    return data;
  },

  async getHealthStatus(): Promise<{
    status: string;
    version: string;
    uptime: number;
    timestamp: string;
  }> {
    const { data } = await api.get('/health');
    return data;
  },
};