import React from 'react';
import { Activity, CheckCircle, XCircle, FileCode, CheckSquare, GitCommit, RefreshCw } from 'lucide-react';
import type { ProjectHealth } from '../types';

interface HealthDashboardProps {
  health: ProjectHealth | null;
  onRefresh: () => void;
  isLoading: boolean;
}

export const HealthDashboard: React.FC<HealthDashboardProps> = ({ health, onRefresh, isLoading }) => {
  if (!health) {
    return (
      <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex items-center justify-center min-h-[140px]">
        <div className="text-slate-400 flex items-center gap-2 text-sm">
          <Activity className="w-4 h-4 animate-pulse text-indigo-400" />
          <span>Connect a repository to inspect project health and test metrics...</span>
        </div>
      </div>
    );
  }

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 70) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    if (score >= 50) return 'text-orange-400 border-orange-500/30 bg-orange-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  return (
    <div className="glass-panel rounded-2xl p-5 border border-slate-800 shadow-xl shadow-black/30">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 text-indigo-400" />
          <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider">Project Health Dashboard</h2>
        </div>
        <button
          onClick={onRefresh}
          disabled={isLoading}
          className="text-xs text-slate-400 hover:text-indigo-400 flex items-center gap-1.5 transition-colors cursor-pointer"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin text-indigo-400' : ''}`} />
          <span>Refresh Metrics</span>
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
        {/* Health Score */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium">Health Score</span>
          <div className="my-1.5 flex items-baseline gap-1.5">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.health_score}</span>
            <span className="text-xs text-slate-500">/ 100</span>
          </div>
          <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border w-fit ${getScoreColor(health.health_score)}`}>
            {health.rating}
          </span>
        </div>

        {/* Tests */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>Test Suite</span>
            {health.tests.failed > 0 ? (
              <XCircle className="w-3.5 h-3.5 text-rose-400" />
            ) : (
              <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            )}
          </span>
          <div className="my-1.5 flex items-baseline gap-1">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.tests.pass_percentage}%</span>
            <span className="text-xs text-slate-400">Pass</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center gap-2">
            <span className="text-emerald-400 font-semibold">{health.tests.passed} Pass</span>
            <span>•</span>
            <span className={health.tests.failed > 0 ? "text-rose-400 font-semibold" : "text-slate-500"}>
              {health.tests.failed} Fail
            </span>
          </div>
        </div>

        {/* Code Issues */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>Code Issues</span>
            <FileCode className="w-3.5 h-3.5 text-purple-400" />
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.code_issues.total}</span>
          </div>
          <div className="text-[11px] text-slate-400 flex items-center gap-1.5">
            <span className="text-rose-400 font-medium">{health.code_issues.high} High</span>
            <span>•</span>
            <span className="text-amber-400 font-medium">{health.code_issues.medium} Med</span>
          </div>
        </div>

        {/* Pending TODOs */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>TODOs & Tasks</span>
            <CheckSquare className="w-3.5 h-3.5 text-amber-400" />
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.todos}</span>
          </div>
          <span className="text-[11px] text-slate-500">In source comments</span>
        </div>

        {/* Recent Commits */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>Recent Commits</span>
            <GitCommit className="w-3.5 h-3.5 text-blue-400" />
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.recent_commits}</span>
          </div>
          <span className="text-[11px] text-slate-500">Active branch</span>
        </div>

        {/* Open Issues */}
        <div className="bg-slate-900/80 border border-slate-800/80 rounded-xl p-3.5 flex flex-col justify-between">
          <span className="text-xs text-slate-400 font-medium flex items-center justify-between">
            <span>Open Issues</span>
            <XCircle className="w-3.5 h-3.5 text-rose-400" />
          </span>
          <div className="my-1.5">
            <span className="text-2xl font-bold text-slate-100 font-mono">{health.open_issues}</span>
          </div>
          <span className="text-[11px] text-slate-500">GitHub Tracker</span>
        </div>
      </div>
    </div>
  );
};
