import React, { useEffect, useState } from 'react';
import {
  Layers,
  CheckCircle2,
  ShieldBan,
  Repeat,
  Clock,
  AlertTriangle,
  Play,
  ArrowRight,
  RefreshCw,
  Sparkles,
} from 'lucide-react';
import { AnalyticsData, Workflow } from '../types';
import { api } from '../services/api';

interface DashboardPageProps {
  onSelectWorkflow: (id: string) => void;
  onNavigateTab: (tab: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  onSelectWorkflow,
  onNavigateTab,
}) => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [launchingScenario, setLaunchingScenario] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [analyticsData, wfList] = await Promise.all([
        api.getAnalytics(),
        api.listWorkflows(),
      ]);
      setAnalytics(analyticsData);
      setWorkflows(wfList.slice(0, 8));
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleQuickLaunch = async (scenario: string, task: string) => {
    try {
      setLaunchingScenario(scenario);
      const newWf = await api.createWorkflow({
        task,
        agent_type: scenario,
      });
      onSelectWorkflow(newWf.id);
    } catch (err) {
      console.error('Failed to quick launch workflow:', err);
    } finally {
      setLaunchingScenario(null);
    }
  };

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
    <div className="space-y-8 animate-fadeIn">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            Safety Operations Center
            <span className="text-xs font-normal text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 live-indicator"></span>
              Live Interception
            </span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time supervisor monitoring AI agent tool calls, cyclic patterns, and execution limits.
          </p>
        </div>
        <div className="flex gap-2">
          <button
            id="refresh-dashboard-btn"
            onClick={fetchData}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800/80 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
          <button
            id="create-workflow-header-btn"
            onClick={() => onNavigateTab('create')}
            className="flex items-center gap-2 px-4 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-lg shadow-indigo-600/30 transition"
          >
            <Play className="w-3.5 h-3.5" />
            Launch Workflow
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Total Runs</span>
            <Layers className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-2xl font-bold text-white">{analytics?.total_workflows ?? 0}</div>
          <div className="text-[11px] text-slate-500 mt-1">Tracked workflows</div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Successful</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold text-emerald-400">{analytics?.successful_workflows ?? 0}</div>
          <div className="text-[11px] text-slate-500 mt-1">Safely completed</div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Blocked</span>
            <ShieldBan className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold text-rose-400">{analytics?.blocked_workflows ?? 0}</div>
          <div className="text-[11px] text-slate-500 mt-1">Halted by safety gate</div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Loops Prevented</span>
            <Repeat className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold text-cyan-400">{analytics?.loop_detected_workflows ?? 0}</div>
          <div className="text-[11px] text-slate-500 mt-1">Cyclic loops broken</div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Approvals</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold text-amber-400">{analytics?.approval_pending_count ?? 0}</div>
          <div className="text-[11px] text-slate-500 mt-1">Awaiting human review</div>
        </div>

        <div className="glass-panel p-4 rounded-xl border border-slate-800/80">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs uppercase font-mono tracking-wider">Avg Duration</span>
            <Clock className="w-4 h-4 text-slate-400" />
          </div>
          <div className="text-2xl font-bold text-white">{analytics?.avg_duration_seconds ?? 0}s</div>
          <div className="text-[11px] text-slate-500 mt-1">Per workflow</div>
        </div>
      </div>

      {/* Quick Interactive Scenario Launchers */}
      <div className="glass-panel p-5 rounded-2xl border border-slate-800/80 relative overflow-hidden">
        <div className="flex items-center gap-2 mb-3">
          <Sparkles className="w-4 h-4 text-indigo-400" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300">
            One-Click Test Scenarios (Instant Safety Engine Verification)
          </h2>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
          <button
            id="scenario-normal-btn"
            onClick={() => handleQuickLaunch('mock:normal_success', 'Audit engineering personnel and compile report')}
            disabled={launchingScenario !== null}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-emerald-500/40 text-left transition group"
          >
            <div className="flex items-center justify-between text-emerald-400 mb-1">
              <span className="text-xs font-semibold">Normal Workflow</span>
              <Play className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:translate-x-0.5 transition" />
            </div>
            <p className="text-[11px] text-slate-400">3-step progression (search &rarr; details &rarr; report) completing safely.</p>
          </button>

          <button
            id="scenario-loop-btn"
            onClick={() => handleQuickLaunch('mock:infinite_loop', 'Synchronize cluster node cache across endpoints')}
            disabled={launchingScenario !== null}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-rose-500/40 text-left transition group"
          >
            <div className="flex items-center justify-between text-rose-400 mb-1">
              <span className="text-xs font-semibold">Cyclic Loop</span>
              <Repeat className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:rotate-45 transition" />
            </div>
            <p className="text-[11px] text-slate-400">A &rarr; B &rarr; A &rarr; B pattern triggers loop detector and blocks run.</p>
          </button>

          <button
            id="scenario-repeat-btn"
            onClick={() => handleQuickLaunch('mock:repeated_calls', 'Locate John Doe in system directory')}
            disabled={launchingScenario !== null}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-amber-500/40 text-left transition group"
          >
            <div className="flex items-center justify-between text-amber-400 mb-1">
              <span className="text-xs font-semibold">Repeated Calls</span>
              <Layers className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 group-hover:scale-110 transition" />
            </div>
            <p className="text-[11px] text-slate-400">Identical arguments called consecutively trigger repeated-call halt.</p>
          </button>

          <button
            id="scenario-sensitive-btn"
            onClick={() => handleQuickLaunch('mock:sensitive_action', 'Update Elena Rostova annual salary in HR database')}
            disabled={launchingScenario !== null}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-indigo-500/40 text-left transition group"
          >
            <div className="flex items-center justify-between text-indigo-400 mb-1">
              <span className="text-xs font-semibold">Sensitive Approval</span>
              <AlertTriangle className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition" />
            </div>
            <p className="text-[11px] text-slate-400">Routes to Approval Center, pauses execution for reviewer sign-off.</p>
          </button>

          <button
            id="scenario-progress-btn"
            onClick={() => handleQuickLaunch('mock:no_progress', 'Fetch status ping from dormant endpoint')}
            disabled={launchingScenario !== null}
            className="p-3.5 rounded-xl border border-slate-800 bg-slate-900/60 hover:bg-slate-800/80 hover:border-cyan-500/40 text-left transition group"
          >
            <div className="flex items-center justify-between text-cyan-400 mb-1">
              <span className="text-xs font-semibold">No-Progress Stagnant</span>
              <ShieldBan className="w-3.5 h-3.5 opacity-60 group-hover:opacity-100 transition" />
            </div>
            <p className="text-[11px] text-slate-400">Repeated stagnant output with zero delta triggers no-progress halt.</p>
          </button>
        </div>
      </div>

      {/* Main Grid: Workflows & Safety Events */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Workflows */}
        <div className="lg:col-span-2 glass-panel p-5 rounded-2xl border border-slate-800/80 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-white">Recent Workflows</h2>
              <button
                id="view-all-workflows-btn"
                onClick={() => onNavigateTab('workflows')}
                className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
              >
                View all <ArrowRight className="w-3 h-3" />
              </button>
            </div>

            {workflows.length === 0 ? (
              <div className="text-center py-10 text-slate-500 text-sm">
                No workflows recorded yet. Launch one of the test scenarios above!
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="text-[11px] uppercase tracking-wider text-slate-400 border-b border-slate-800">
                    <tr>
                      <th className="py-2.5 px-3">Status</th>
                      <th className="py-2.5 px-3">Task Objective</th>
                      <th className="py-2.5 px-3">Agent</th>
                      <th className="py-2.5 px-3">Steps</th>
                      <th className="py-2.5 px-3">Duration</th>
                      <th className="py-2.5 px-3 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 font-mono">
                    {workflows.map((wf) => (
                      <tr
                        key={wf.id}
                        className="hover:bg-slate-800/40 transition cursor-pointer"
                        onClick={() => onSelectWorkflow(wf.id)}
                      >
                        <td className="py-3 px-3">{getStatusBadge(wf.status)}</td>
                        <td className="py-3 px-3 font-sans text-slate-200 font-medium max-w-[220px] truncate">
                          {wf.task}
                        </td>
                        <td className="py-3 px-3 text-slate-400 text-[11px]">
                          {wf.agent_type.replace('mock:', '')}
                        </td>
                        <td className="py-3 px-3 text-slate-300">{wf.step_count}</td>
                        <td className="py-3 px-3 text-slate-400">{wf.execution_duration_seconds}s</td>
                        <td className="py-3 px-3 text-right">
                          <button
                            id={`view-wf-${wf.id.substring(0, 8)}`}
                            className="px-2.5 py-1 rounded bg-slate-800 hover:bg-indigo-600 text-slate-300 hover:text-white transition text-[11px]"
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

        {/* Recent Safety Alerts */}
        <div className="glass-panel p-5 rounded-2xl border border-slate-800/80">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold text-white">Recent Safety Alerts</h2>
            <button
              id="view-all-alerts-btn"
              onClick={() => onNavigateTab('safety-events')}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
            >
              All Alerts <ArrowRight className="w-3 h-3" />
            </button>
          </div>

          {!analytics?.recent_events || analytics.recent_events.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-xs">
              No safety violations detected recently.
            </div>
          ) : (
            <div className="space-y-3">
              {analytics.recent_events.slice(0, 5).map((evt) => (
                <div
                  key={evt.id}
                  className="p-3 rounded-xl border border-slate-800 bg-slate-900/40 hover:bg-slate-800/60 transition cursor-pointer"
                  onClick={() => onSelectWorkflow(evt.workflow_id)}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-[10px] font-bold uppercase px-1.5 py-0.5 rounded ${
                      evt.severity === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                      evt.severity === 'HIGH' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                      'bg-slate-800 text-slate-300'
                    }`}>
                      {evt.severity}
                    </span>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(evt.created_at).toLocaleTimeString()}
                    </span>
                  </div>
                  <div className="text-xs font-semibold text-slate-200 mt-1">
                    {evt.rule_name}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-0.5 line-clamp-2">
                    Decision: <strong className="text-rose-400 font-mono">{evt.decision}</strong> &mdash; intercepted in workflow {evt.workflow_id.substring(0, 8)}...
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
