import React from 'react';
import { Box, X } from 'lucide-react';
import type { MCPToolInfo } from '../types';

interface ToolsModalProps {
  isOpen: boolean;
  onClose: () => void;
  tools: MCPToolInfo[];
}

export const ToolsModal: React.FC<ToolsModalProps> = ({ isOpen, onClose, tools }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-3xl w-full p-6 max-h-[85vh] flex flex-col shadow-2xl">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center">
              <Box className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-100">Registered Model Context Protocol (MCP) Tools</h3>
              <p className="text-xs text-slate-400">Exposed by FastMCP Server to the Gemini AI Agent</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="overflow-y-auto my-4 space-y-3 pr-2">
          {tools.map((t) => (
            <div key={t.name} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
              <div className="flex items-center justify-between mb-1">
                <span className="font-mono text-sm font-semibold text-indigo-300">{t.name}</span>
                <span className="text-[10px] uppercase font-semibold px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                  MCP Tool
                </span>
              </div>
              <p className="text-xs text-slate-300 mb-2">{t.description}</p>
              {t.input_schema && t.input_schema.properties && (
                <div className="text-[11px] text-slate-400 font-mono bg-slate-900 p-2 rounded border border-slate-800/60">
                  <span className="text-slate-500 block mb-1">Parameters:</span>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(t.input_schema.properties).map(([param, prop]: [string, any]) => (
                      <span key={param} className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
                        {param}: <span className="text-indigo-400">{prop.type || 'any'}</span>
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="pt-3 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition-colors cursor-pointer"
          >
            Close Catalog
          </button>
        </div>
      </div>
    </div>
  );
};
