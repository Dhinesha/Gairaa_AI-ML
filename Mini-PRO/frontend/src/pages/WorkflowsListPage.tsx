import React, { useEffect, useState } from 'react';
import { Layers, Search, Filter, Play, RefreshCw, ArrowRight } from 'lucide-react';
import { Workflow } from '../types';
import { api } from '../services/api';

interface WorkflowsListPageProps {
  onSelectWorkflow: (id: string) => void;
  onNavigateCreate: () => void;
}

export const WorkflowsListPage: React.FC<WorkflowsListPageProps> = ({
  onSelectWorkflow,
  onNavigateCreate,
}) => {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      const data = await api.listWorkflows(statusFilter === 'ALL' ? undefined : statusFilter);
      setWorkflows(data);
    } catch (err) {
      console.error('Error fetching workflows:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, [statusFilter]);

  const filtered = workflows.filter((w) =>
    w.task.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
    w.agent_type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'COMPLETED':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">COMPLETED</span>;
      case 'BLOCKED':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-rose-500/10 text-rose-400 border border-rose-500/20">BLOCKED</span>;
      case 'PAUSED_APPROVAL':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-amber-500/10 text-amber-400 border border-amber-500/20">APPROVAL REQUIRED</span>;
      case 'RUNNING':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 animate-pulse">RUNNING</span>;
      case 'STOPPED':
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-500/10 text-slate-400 border border-slate-500/20">STOPPED</span>;
      default:
        return <span className="px-2 py-0.5 rounded text-xs font-medium bg-slate-800 text-slate-300">{status}</span>;
    }
  };

  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <Layers className="w-6 h-6 text-indigo-400" />
            Workflow Executions
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Historical trace and live monitoring of all AI agent workflows.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            id="refresh-workflows-btn"
            onClick={fetchWorkflows}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            id="create-new-workflow-btn"
            onClick={onNavigateCreate}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Play className="w-3.5 h-3.5" />
            New Workflow
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3 items-center justify-between glass-panel p-3 rounded-xl border border-slate-800">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            id="workflow-search-input"
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by task, agent or ID..."
            className="w-full pl-9 pr-4 py-1.5 rounded-lg bg-slate-900 border border-slate-700 text-white text-xs placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          />
        </div>

        {/* Status Filters */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full sm:w-auto">
          {['ALL', 'COMPLETED', 'BLOCKED', 'PAUSED_APPROVAL', 'RUNNING'].map((status) => (
            <button
              key={status}
              id={`filter-${status.toLowerCase()}`}
              onClick={() => setStatusFilter(status)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition ${
                statusFilter === status
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {status.replace('_', ' ')}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden">
        {loading && workflows.length === 0 ? (
          <div className="py-20 text-center text-slate-400 text-sm">Loading workflows...</div>
        ) : filtered.length === 0 ? (
          <div className="py-20 text-center text-slate-400 text-sm">
            No workflows found matching current criteria.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800 bg-slate-900/60">
                <tr>
                  <th className="py-3 px-4">Status</th>
                  <th className="py-3 px-4">Task</th>
                  <th className="py-3 px-4">Agent Profile</th>
                  <th className="py-3 px-4">Steps</th>
                  <th className="py-3 px-4">Duration</th>
                  <th className="py-3 px-4">Created</th>
                  <th className="py-3 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {filtered.map((wf) => (
                  <tr
                    key={wf.id}
                    className="hover:bg-slate-800/40 transition cursor-pointer"
                    onClick={() => onSelectWorkflow(wf.id)}
                  >
                    <td className="py-3.5 px-4">{getStatusBadge(wf.status)}</td>
                    <td className="py-3.5 px-4 font-sans text-slate-200 font-medium max-w-sm truncate">
                      {wf.task}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 text-[11px]">
                      {wf.agent_type}
                    </td>
                    <td className="py-3.5 px-4 text-slate-300 font-semibold">
                      {wf.step_count}
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {wf.execution_duration_seconds}s
                    </td>
                    <td className="py-3.5 px-4 text-slate-500 text-[11px]">
                      {new Date(wf.created_at).toLocaleString()}
                    </td>
                    <td className="py-3.5 px-4 text-right font-sans">
                      <button
                        id={`inspect-btn-${wf.id.substring(0, 8)}`}
                        className="px-3 py-1 rounded bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition text-xs font-medium"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
