import React from 'react';
import { Cpu, Sparkles, Box, GitBranch } from 'lucide-react';
import type { SystemHealth } from '../types';

interface HeaderProps {
  systemHealth: SystemHealth | null;
  onOpenToolsModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({ systemHealth, onOpenToolsModal }) => {
  return (
    <header className="border-b border-slate-800/80 bg-slate-950/70 backdrop-blur-md sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Title */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
            <Cpu className="w-6 h-6 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-lg font-bold text-white tracking-tight">AI DevOps Assistant</h1>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-indigo-500/20 text-indigo-400 border border-indigo-500/30">
                MCP Powered
              </span>
            </div>
            <p className="text-xs text-slate-400">Model Context Protocol • Autonomous Developer Agent</p>
          </div>
        </div>

        {/* System Health Status Pills */}
        <div className="flex items-center space-x-3">
          {/* MCP Server Badge */}
          <button
            onClick={onOpenToolsModal}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/50 transition-colors text-xs text-slate-300 group cursor-pointer"
            title="Click to view all MCP tools"
          >
            <Box className="w-3.5 h-3.5 text-indigo-400 group-hover:rotate-12 transition-transform" />
            <span>MCP Server:</span>
            <span className="font-semibold text-emerald-400 flex items-center gap-1">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              {systemHealth?.mcp_server?.tools_count ?? 12} Tools
            </span>
          </button>

          {/* Gemini AI Status */}
          <div className="hidden sm:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            <span>LLM:</span>
            <span className="font-semibold text-purple-300">
              {systemHealth?.gemini_api?.configured ? 'Gemini 2.5' : 'Smart Agent'}
            </span>
          </div>

          {/* GitHub Status */}
          <div className="hidden md:flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <GitBranch className="w-3.5 h-3.5 text-slate-400" />
            <span>GitHub:</span>
            <span className="font-semibold text-emerald-400">Connected</span>
          </div>
        </div>
      </div>
    </header>
  );
};
