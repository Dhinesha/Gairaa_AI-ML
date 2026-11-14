import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  PieChart as PieIcon,
  ShieldAlert,
  Clock,
  RefreshCw,
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { AnalyticsData } from '../types';
import { api } from '../services/api';

const STATUS_COLORS: Record<string, string> = {
  Completed: '#10B981',
  Blocked: '#F43F5E',
  'Paused Approval': '#F59E0B',
  Running: '#38BDF8',
  Failed: '#94A3B8',
};

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: '#F43F5E',
  HIGH: '#F59E0B',
  WARNING: '#EAB308',
  INFO: '#6366F1',
};

export const AnalyticsPage: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const res = await api.getAnalytics();
      setData(res);
    } catch (err) {
      console.error('Error fetching analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const pieData = data ? [
    { name: 'Completed', value: data.successful_workflows },
    { name: 'Blocked', value: data.blocked_workflows },
    { name: 'Paused Approval', value: data.approval_pending_count },
    { name: 'Running', value: data.running_workflows },
    { name: 'Failed', value: data.failed_workflows },
  ].filter(d => d.value > 0) : [];

  const toolBarData = data?.tool_distribution
    ? Object.entries(data.tool_distribution).map(([tool, count]) => ({
        tool: tool.length > 15 ? tool.substring(0, 15) + '...' : tool,
        count,
      }))
    : [];

  const severityBarData = data?.severity_distribution
    ? Object.entries(data.severity_distribution).map(([sev, count]) => ({
        severity: sev,
        count,
        fill: SEVERITY_COLORS[sev] || '#6366F1',
      }))
    : [];

  const successRate = data?.total_workflows
    ? Math.round((data.successful_workflows / data.total_workflows) * 100)
    : 0;

  const loopPreventionRate = data?.total_workflows
    ? Math.round((data.loop_detected_workflows / data.total_workflows) * 100)
    : 0;

  return (
    <div className="space-y-8 animate-fadeIn max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <BarChart3 className="w-6 h-6 text-indigo-400" />
            Safety Engine & Workflow Analytics
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Aggregated metrics derived in real-time from backend database records and audit trails.
          </p>
        </div>
        <button
          id="refresh-analytics-btn"
          onClick={fetchAnalytics}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] uppercase font-mono text-slate-400 block mb-1">
            Success Rate
          </span>
          <div className="text-3xl font-extrabold text-emerald-400">{successRate}%</div>
          <p className="text-[11px] text-slate-500 mt-1">Safely completed workflows</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] uppercase font-mono text-slate-400 block mb-1">
            Loops Broken
          </span>
          <div className="text-3xl font-extrabold text-cyan-400">{data?.loop_detected_workflows ?? 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Infinite cycles intercepted</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] uppercase font-mono text-slate-400 block mb-1">
            Blocked Workflows
          </span>
          <div className="text-3xl font-extrabold text-rose-400">{data?.blocked_workflows ?? 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Limits / repeats violated</p>
        </div>

        <div className="glass-panel p-5 rounded-2xl border border-slate-800">
          <span className="text-[11px] uppercase font-mono text-slate-400 block mb-1">
            Average Run Time
          </span>
          <div className="text-3xl font-extrabold text-white">{data?.avg_duration_seconds ?? 0}s</div>
          <p className="text-[11px] text-slate-500 mt-1">Across all completed tasks</p>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Workflow Outcome Distribution */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <PieIcon className="w-4 h-4 text-emerald-400" /> Workflow Execution Outcomes
          </h2>
          <div className="h-64 w-full">
            {pieData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                No workflow outcomes to visualize yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={STATUS_COLORS[entry.name] || '#6366F1'}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: '#1E293B',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Top Tools Executed */}
        <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-cyan-400" /> Tool Invocation Volume
          </h2>
          <div className="h-64 w-full">
            {toolBarData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                No tool calls recorded yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={toolBarData}>
                  <XAxis dataKey="tool" stroke="#64748B" fontSize={10} />
                  <YAxis stroke="#64748B" fontSize={10} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: '#1E293B',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="count" fill="#6366F1" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* Safety Events by Severity */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-rose-400" /> Safety Events by Severity
          </h2>
          <div className="h-56 w-full">
            {severityBarData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-slate-500 text-xs">
                No safety events recorded yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={severityBarData}>
                  <XAxis dataKey="severity" stroke="#64748B" fontSize={11} />
                  <YAxis stroke="#64748B" fontSize={11} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#0F172A',
                      borderColor: '#1E293B',
                      borderRadius: '0.75rem',
                      fontSize: '12px',
                    }}
                  />
                  <Bar dataKey="count" fill="#F43F5E" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
