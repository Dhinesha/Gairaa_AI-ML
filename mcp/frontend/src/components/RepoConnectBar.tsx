import React, { useState } from 'react';
import { GitBranch, Star, GitFork, AlertCircle, CheckCircle2, Lock, ArrowRight, Loader2, Sparkles, X } from 'lucide-react';
import type { RepositoryInfo } from '../types';

interface RepoConnectBarProps {
  currentRepo: RepositoryInfo | null;
  onConnect: (url: string, token?: string) => Promise<void>;
  isLoading: boolean;
  errorMessage: string | null;
  onClearError: () => void;
}

export const RepoConnectBar: React.FC<RepoConnectBarProps> = ({
  currentRepo,
  onConnect,
  isLoading,
  errorMessage,
  onClearError
}) => {
  const [repoUrl, setRepoUrl] = useState('demo/demo_repo');
  const [token, setToken] = useState('');
  const [showTokenInput, setShowTokenInput] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (repoUrl.trim()) {
      onClearError();
      onConnect(repoUrl.trim(), token.trim() || undefined);
    }
  };

  const loadPreset = (preset: string) => {
    setRepoUrl(preset);
    onClearError();
    onConnect(preset, token.trim() || undefined);
  };

  return (
    <div className="glass-panel rounded-2xl p-5 shadow-xl shadow-black/40 border border-slate-800">
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        {/* Connection Form */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-2">
            <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
              <span>GitHub Repository Connection</span>
              <span className="w-1.5 h-1.5 rounded-full bg-indigo-400"></span>
            </label>
            <button
              type="button"
              onClick={() => setShowTokenInput(!showTokenInput)}
              className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 transition-colors cursor-pointer"
            >
              <Lock className="w-3 h-3" />
              {showTokenInput ? 'Hide Token' : 'Add GitHub Token (for Private Repos)'}
            </button>
          </div>

          <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={repoUrl}
                onChange={(e) => {
                  setRepoUrl(e.target.value);
                  if (errorMessage) onClearError();
                }}
                placeholder="e.g. https://github.com/owner/project or owner/project"
                className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-mono"
              />
            </div>

            {showTokenInput && (
              <div className="sm:w-64">
                <input
                  type="password"
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  placeholder="ghp_personal_token"
                  className="w-full bg-slate-900/90 border border-slate-700/80 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all font-mono"
                />
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading || !repoUrl.trim()}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white font-medium text-sm shadow-md shadow-indigo-500/20 disabled:opacity-50 flex items-center justify-center gap-2 transition-all cursor-pointer whitespace-nowrap"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Connecting...</span>
                </>
              ) : (
                <>
                  <span>Connect Repository</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Inline Error Notice */}
          {errorMessage && (
            <div className="mt-3 p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-300 flex items-start justify-between gap-2">
              <div className="flex items-start gap-2">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <div className="space-y-1">
                  <p className="font-semibold text-rose-200">Unable to access repository</p>
                  <p className="text-slate-300 whitespace-pre-line">{errorMessage}</p>
                  <p className="text-slate-400 text-[11px] pt-1">
                    💡 If this repository is <strong>Private</strong>, click <strong>"Add GitHub Token"</strong> above and enter your GitHub PAT (<code className="text-indigo-300">ghp_...</code>) with <code className="text-indigo-300">repo</code> scope.
                  </p>
                </div>
              </div>
              <button
                onClick={onClearError}
                className="text-rose-400 hover:text-rose-200 p-1 rounded transition-colors cursor-pointer"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {/* Preset Quick Chips */}
          <div className="flex items-center gap-2 mt-3 flex-wrap text-xs text-slate-400">
            <span className="text-slate-500">Quick Demo Presets:</span>
            <button
              type="button"
              onClick={() => loadPreset('demo/demo_repo')}
              className="px-2.5 py-1 rounded-lg bg-indigo-950/60 hover:bg-indigo-900/80 text-indigo-300 border border-indigo-800/60 transition-colors cursor-pointer flex items-center gap-1 font-medium"
            >
              <Sparkles className="w-3 h-3 text-indigo-400" />
              Demo Repo (auth.py & failing tests)
            </button>
            <button
              type="button"
              onClick={() => loadPreset('Dhinesha/agroguide-ai')}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 transition-colors cursor-pointer"
            >
              Dhinesha/agroguide-ai
            </button>
            <button
              type="button"
              onClick={() => loadPreset('Dhinesha/medprescription-ai')}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 transition-colors cursor-pointer"
            >
              Dhinesha/medprescription-ai
            </button>
            <button
              type="button"
              onClick={() => loadPreset('octocat/Hello-World')}
              className="px-2.5 py-1 rounded-lg bg-slate-800/60 hover:bg-slate-700/80 text-slate-300 border border-slate-700/60 transition-colors cursor-pointer"
            >
              octocat/Hello-World
            </button>
          </div>
        </div>

        {/* Current Active Repo Card */}
        {currentRepo && (
          <div className="lg:w-80 bg-slate-900/60 border border-slate-800 rounded-xl p-3.5 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Connected
              </span>
              <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 flex items-center gap-1">
                <GitBranch className="w-3 h-3 text-indigo-400" />
                {currentRepo.default_branch}
              </span>
            </div>

            <div className="mt-1.5">
              <h3 className="font-semibold text-slate-100 text-sm truncate" title={`${currentRepo.owner}/${currentRepo.repo}`}>
                {currentRepo.owner}/{currentRepo.repo}
              </h3>
              <p className="text-xs text-slate-400 line-clamp-1 mt-0.5" title={currentRepo.description}>
                {currentRepo.description || 'No description provided'}
              </p>
            </div>

            <div className="flex items-center gap-4 mt-2.5 pt-2 border-t border-slate-800/80 text-xs text-slate-400">
              <div className="flex items-center gap-1">
                <Star className="w-3.5 h-3.5 text-amber-400" />
                <span>{currentRepo.stars}</span>
              </div>
              <div className="flex items-center gap-1">
                <GitFork className="w-3.5 h-3.5 text-slate-400" />
                <span>{currentRepo.forks}</span>
              </div>
              <div className="flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 text-rose-400" />
                <span>{currentRepo.open_issues} issues</span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
