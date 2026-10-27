import type { RepositoryInfo, ChatMessage, ChatResponse, ProjectHealth, SystemHealth, MCPToolInfo } from '../types';

const API_BASE = '/api';

export const api = {
  async getHealthCheck(): Promise<SystemHealth> {
    const res = await fetch(`${API_BASE}/health-check`);
    if (!res.ok) throw new Error('Failed to fetch system health');
    return res.json();
  },

  async connectRepo(repoUrl: string, token?: string): Promise<{ status: string; repository: RepositoryInfo }> {
    const res = await fetch(`${API_BASE}/connect`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ repo_url: repoUrl, token: token || undefined }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to connect repository' }));
      throw new Error(err.detail || 'Failed to connect repository');
    }
    return res.json();
  },

  async sendMessage(message: string, history: ChatMessage[], repoUrl?: string): Promise<ChatResponse> {
    const payload = {
      message,
      history: history.map(h => ({ role: h.role, content: h.content })),
      repo_url: repoUrl,
    };
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Chat request failed' }));
      throw new Error(err.detail || 'Chat request failed');
    }
    return res.json();
  },

  async confirmAction(actionId: string, confirmed: boolean): Promise<any> {
    const res = await fetch(`${API_BASE}/confirm`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action_id: actionId, confirmed }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to execute confirmed action' }));
      throw new Error(err.detail || 'Confirmation failed');
    }
    return res.json();
  },

  async getRepoHealth(): Promise<ProjectHealth> {
    const res = await fetch(`${API_BASE}/repo-health`);
    if (!res.ok) throw new Error('Failed to fetch project health');
    return res.json();
  },

  async getTools(): Promise<MCPToolInfo[]> {
    const res = await fetch(`${API_BASE}/tools`);
    if (!res.ok) throw new Error('Failed to fetch tools');
    return res.json();
  },
};
