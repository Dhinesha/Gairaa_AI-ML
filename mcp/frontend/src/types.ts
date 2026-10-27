export interface RepositoryInfo {
  owner: string;
  repo: string;
  name: string;
  description?: string;
  default_branch: string;
  stars: number;
  forks: number;
  open_issues: number;
  url?: string;
  is_local_demo?: boolean;
}

export interface ChatMessage {
  id?: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp?: string;
  tool_executions?: ToolCallLog[];
  requires_confirmation?: boolean;
  pending_action?: PendingAction;
}

export interface ToolCallLog {
  id: string;
  tool_name: string;
  arguments: Record<string, any>;
  status: 'pending' | 'running' | 'success' | 'error';
  result?: any;
  error?: string;
  duration_ms?: number;
}

export interface PendingAction {
  action_id: string;
  tool_name: string;
  action_type: string;
  description: string;
  arguments: {
    owner: string;
    repo: string;
    title: string;
    body: string;
    [key: string]: any;
  };
}

export interface ChatResponse {
  message: string;
  tool_executions: ToolCallLog[];
  requires_confirmation?: boolean;
  pending_action?: PendingAction;
}

export interface ProjectHealth {
  repository: string;
  total_files: number;
  python_files: number;
  test_files: number;
  tests: {
    total: number;
    passed: number;
    failed: number;
    pass_percentage: number;
  };
  code_issues: {
    high: number;
    medium: number;
    low: number;
    total: number;
  };
  todos: number;
  recent_commits: number;
  open_issues: number;
  health_score: number;
  rating: string;
}

export interface SystemHealth {
  status: string;
  mcp_server: {
    status: string;
    name: string;
    tools_count: number;
  };
  gemini_api: {
    configured: boolean;
    model: string;
  };
  github_api: {
    token_configured: boolean;
    rate_limit_authenticated: boolean;
  };
  active_repo: {
    url: string;
    owner: string;
    repo: string;
    info?: RepositoryInfo;
  };
}

export interface MCPToolInfo {
  name: string;
  description: string;
  input_schema: any;
}
