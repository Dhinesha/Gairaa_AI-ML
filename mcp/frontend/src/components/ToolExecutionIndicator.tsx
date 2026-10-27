import React, { useState } from 'react';
import { CheckCircle2, Loader2, Circle, AlertCircle, ChevronDown, ChevronRight, Clock, Box } from 'lucide-react';
import type { ToolCallLog } from '../types';

interface ToolExecutionIndicatorProps {
  toolExecutions: ToolCallLog[];
  isThinking: boolean;
}

export const ToolExecutionIndicator: React.FC<ToolExecutionIndicatorProps> = ({ toolExecutions, isThinking }) => {
  const [expandedId, setExpandedId] = useState<string | null>(null);

  if (toolExecutions.length === 0 && !isThinking) {
    return null;
  }

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3.5 my-3 shadow-md shadow-black/20">
      <div className="flex items-center justify-between pb-2 border-b border-slate-800/80">
        <div className="flex items-center gap-2">
          <Box className="w-4 h-4 text-indigo-400" />
          <span className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            MCP Tool Pipeline
          </span>
        </div>
        {isThinking ? (
          <div className="flex items-center gap-1.5 text-xs text-indigo-400 animate-pulse font-medium">
            <Loader2 className="w-3.5 h-3.5 animate-spin" />
            <span>AI is working through MCP...</span>
          </div>
        ) : (
          <div className="flex items-center gap-1.5 text-xs text-emerald-400 font-medium">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>All operations completed</span>
          </div>
        )}
      </div>

      <div className="mt-2.5 space-y-1.5">
        {toolExecutions.map((tool) => {
          const isExpanded = expandedId === tool.id;
          return (
            <div
              key={tool.id}
              className="border border-slate-800/80 rounded-lg bg-slate-950/40 hover:bg-slate-950/70 transition-colors overflow-hidden"
            >
              <div
                onClick={() => toggleExpand(tool.id)}
                className="flex items-center justify-between px-3 py-2 cursor-pointer text-xs"
              >
                <div className="flex items-center gap-2">
                  {tool.status === 'success' && (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  )}
                  {tool.status === 'running' && (
                    <Loader2 className="w-3.5 h-3.5 text-indigo-400 animate-spin shrink-0" />
                  )}
                  {tool.status === 'error' && (
                    <AlertCircle className="w-3.5 h-3.5 text-rose-400 shrink-0" />
                  )}
                  {tool.status === 'pending' && (
                    <Circle className="w-3.5 h-3.5 text-slate-500 shrink-0" />
                  )}

                  <span className="font-mono font-medium text-slate-200">{tool.tool_name}</span>
                </div>

                <div className="flex items-center gap-2 text-slate-400">
                  {tool.duration_ms !== undefined && (
                    <span className="text-[11px] font-mono text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {tool.duration_ms}ms
                    </span>
                  )}
                  {isExpanded ? (
                    <ChevronDown className="w-3.5 h-3.5 text-slate-400" />
                  ) : (
                    <ChevronRight className="w-3.5 h-3.5 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="px-3 py-2.5 bg-slate-950/80 border-t border-slate-800 text-xs font-mono space-y-2">
                  <div>
                    <span className="text-slate-500 block mb-1">Arguments:</span>
                    <pre className="bg-slate-900/90 p-2 rounded border border-slate-800 text-indigo-300 overflow-x-auto text-[11px]">
                      {JSON.stringify(tool.arguments, null, 2)}
                    </pre>
                  </div>
                  {tool.result !== undefined && (
                    <div>
                      <span className="text-slate-500 block mb-1">Result Payload:</span>
                      <pre className="bg-slate-900/90 p-2 rounded border border-slate-800 text-emerald-300 overflow-x-auto text-[11px] max-h-48">
                        {typeof tool.result === 'object'
                          ? JSON.stringify(tool.result, null, 2)
                          : String(tool.result)}
                      </pre>
                    </div>
                  )}
                  {tool.error && (
                    <div>
                      <span className="text-rose-400 block mb-1">Error:</span>
                      <pre className="bg-rose-950/30 p-2 rounded border border-rose-900/50 text-rose-300 overflow-x-auto text-[11px]">
                        {tool.error}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
