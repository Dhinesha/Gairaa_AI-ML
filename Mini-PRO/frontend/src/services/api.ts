import axios from 'axios';
import {
  AnalyticsData,
  ApprovalRequest,
  CreateWorkflowPayload,
  DatabaseUploadResponse,
  SafetyEvent,
  SafetyPolicyConfig,
  Workflow,
} from '../types';

const API_BASE = '/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
});

export const api = {
  // Workflows
  async listWorkflows(statusFilter?: string): Promise<Workflow[]> {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const res = await apiClient.get<Workflow[]>('/workflows', { params });
    return res.data;
  },

  async getWorkflow(workflowId: string): Promise<Workflow> {
    const res = await apiClient.get<Workflow>(`/workflows/${workflowId}`);
    return res.data;
  },

  async createWorkflow(payload: CreateWorkflowPayload, autoRun: boolean = true): Promise<Workflow> {
    const res = await apiClient.post<Workflow>(`/workflows?auto_run=${autoRun}`, payload);
    return res.data;
  },

  async runWorkflow(workflowId: string): Promise<Workflow> {
    const res = await apiClient.post<Workflow>(`/workflows/${workflowId}/run`);
    return res.data;
  },

  async stopWorkflow(workflowId: string): Promise<Workflow> {
    const res = await apiClient.post<Workflow>(`/workflows/${workflowId}/stop`);
    return res.data;
  },

  async resumeWorkflow(workflowId: string): Promise<Workflow> {
    const res = await apiClient.post<Workflow>(`/workflows/${workflowId}/resume`);
    return res.data;
  },

  async retryWorkflow(workflowId: string): Promise<Workflow> {
    const res = await apiClient.post<Workflow>(`/workflows/${workflowId}/retry`);
    return res.data;
  },

  async getWorkflowEvents(workflowId: string): Promise<SafetyEvent[]> {
    const res = await apiClient.get<SafetyEvent[]>(`/workflows/${workflowId}/events`);
    return res.data;
  },

  // Approvals
  async listApprovals(statusFilter?: string): Promise<ApprovalRequest[]> {
    const params = statusFilter ? { status_filter: statusFilter } : {};
    const res = await apiClient.get<ApprovalRequest[]>('/approvals', { params });
    return res.data;
  },

  async approveAction(
    approvalId: string,
    reviewedBy: string = 'admin-lead',
    comment?: string
  ): Promise<ApprovalRequest> {
    const res = await apiClient.post<ApprovalRequest>(
      `/approvals/${approvalId}/approve`,
      { reviewed_by: reviewedBy, comment },
      { headers: { 'x-user-role': 'admin' } }
    );
    return res.data;
  },

  async rejectAction(
    approvalId: string,
    reviewedBy: string = 'admin-lead',
    comment?: string
  ): Promise<ApprovalRequest> {
    const res = await apiClient.post<ApprovalRequest>(
      `/approvals/${approvalId}/reject`,
      { reviewed_by: reviewedBy, comment },
      { headers: { 'x-user-role': 'admin' } }
    );
    return res.data;
  },

  // Safety & Rules
  async listSafetyEvents(severity?: string): Promise<SafetyEvent[]> {
    const params = severity ? { severity } : {};
    const res = await apiClient.get<SafetyEvent[]>('/safety/events', { params });
    return res.data;
  },

  async getSafetyConfig(): Promise<SafetyPolicyConfig> {
    const res = await apiClient.get<SafetyPolicyConfig>('/safety/config');
    return res.data;
  },

  async updateSafetyConfig(config: SafetyPolicyConfig): Promise<SafetyPolicyConfig> {
    const res = await apiClient.put<SafetyPolicyConfig>('/safety/config', config);
    return res.data;
  },

  async listSafetyRules(): Promise<any[]> {
    const res = await apiClient.get<any[]>('/safety/rules');
    return res.data;
  },

  // Analytics
  async getAnalytics(): Promise<AnalyticsData> {
    const res = await apiClient.get<AnalyticsData>('/analytics');
    return res.data;
  },

  // Health
  async getHealth(): Promise<{ status: string; database_connected: boolean; redis_connected: boolean }> {
    const res = await axios.get('/health');
    return res.data;
  },

  // Native Backend Authentication & User Accounts (SQLite/PostgreSQL safety_engine.db)
  async signUp(data: {
    name: string;
    email: string;
    password: string;
    role: string;
    organization?: string;
  }): Promise<{ id: string; name: string; email: string; role: string; organization: string; is_active: boolean }> {
    const res = await apiClient.post('/auth/signup', data);
    return res.data;
  },

  async login(data: {
    email: string;
    password: string;
    role?: string;
  }): Promise<{ id: string; name: string; email: string; role: string; organization: string; is_active: boolean }> {
    const res = await apiClient.post('/auth/login', data);
    return res.data;
  },

  async listUsers(): Promise<Array<{ id: string; name: string; email: string; role: string; organization: string }>> {
    const res = await apiClient.get('/auth/users');
    return res.data;
  },

  // Database Upload & Inspection (AI Teacher Mode)
  async uploadDatabase(file: File): Promise<DatabaseUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<DatabaseUploadResponse>('/database/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  async getSampleDatabase(preset: string = 'university'): Promise<DatabaseUploadResponse> {
    const res = await apiClient.get<DatabaseUploadResponse>('/database/sample', {
      params: { preset },
    });
    return res.data;
  },
};
