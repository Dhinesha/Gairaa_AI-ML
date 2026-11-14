export type SafetyDecision = 'ALLOW' | 'BLOCK' | 'REQUIRE_APPROVAL';
export type RiskLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type WorkflowStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'BLOCKED' | 'PAUSED_APPROVAL' | 'FAILED' | 'STOPPED';

export interface WorkflowStep {
  id: string;
  step_number: number;
  tool_name: string;
  raw_arguments?: Record<string, any>;
  sanitized_arguments?: Record<string, any>;
  tool_result?: any;
  duration_ms: number;
  status: 'SUCCESS' | 'FAILED' | 'BLOCKED' | 'SKIPPED';
  safety_decision: SafetyDecision;
  rule_triggered?: string;
  risk_level: RiskLevel;
  normalized_hash?: string;
  timestamp: string;
}

export interface SafetyEvent {
  id: string;
  workflow_id: string;
  step_id?: string;
  event_type: string;
  severity: 'INFO' | 'WARNING' | 'HIGH' | 'CRITICAL';
  rule_name: string;
  details?: Record<string, any>;
  decision: SafetyDecision;
  created_at: string;
}

export interface ApprovalRequest {
  id: string;
  workflow_id: string;
  step_id?: string;
  tool_name: string;
  tool_arguments?: Record<string, any>;
  risk_level: RiskLevel;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  reviewed_by?: string;
  reviewed_at?: string;
  comment?: string;
  created_at: string;
}

export interface Workflow {
  id: string;
  task: string;
  agent_type: string;
  status: WorkflowStatus;
  step_count: number;
  config_override?: Record<string, any>;
  result_summary?: string;
  termination_reason?: string;
  error_message?: string;
  execution_duration_seconds: number;
  created_at: string;
  updated_at?: string;
  completed_at?: string;
  steps?: WorkflowStep[];
  events?: SafetyEvent[];
  approvals?: ApprovalRequest[];
}

export interface SafetyPolicyConfig {
  name: string;
  is_active: boolean;
  max_workflow_steps: number;
  max_repeated_calls: number;
  max_execution_duration_seconds: number;
  max_tool_calls: number;
  max_retries: number;
  loop_cycle_threshold: number;
  max_no_progress_steps: number;
  auto_block_no_progress: boolean;
  sensitive_tools: string[];
  sensitive_argument_patterns: string[];
}

export interface AnalyticsData {
  total_workflows: number;
  successful_workflows: number;
  blocked_workflows: number;
  loop_detected_workflows: number;
  approval_pending_count: number;
  failed_workflows: number;
  running_workflows: number;
  avg_duration_seconds: number;
  tool_distribution: Record<string, number>;
  severity_distribution: Record<string, number>;
  recent_events: SafetyEvent[];
}

export interface CreateWorkflowPayload {
  task: string;
  agent_type: string;
  max_steps?: number;
  max_repeated_calls?: number;
  max_duration_seconds?: number;
  loop_cycle_threshold?: number;
}

export interface UserProfile {
  name: string;
  email: string;
  role: 'student' | 'developer' | 'security_lead';
  organization: string;
  avatarColor: string;
  studentModeEnabled: boolean;
  loginTime: string;
}

export interface ColumnInfo {
  name: string;
  type: string;
  is_primary_key: boolean;
  not_null: boolean;
}

export interface TableInfo {
  name: string;
  row_count: number;
  columns: ColumnInfo[];
  preview_rows: Record<string, any>[];
}

export interface DatabaseUploadResponse {
  file_id: string;
  filename: string;
  file_size_bytes: number;
  database_type: string;
  table_count: number;
  total_records: number;
  tables: TableInfo[];
  summary_en: string;
  summary_ta: string;
}


