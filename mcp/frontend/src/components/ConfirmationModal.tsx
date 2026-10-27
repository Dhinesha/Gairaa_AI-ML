import React from 'react';
import { ShieldAlert, Check, X, Loader2, GitBranch } from 'lucide-react';
import type { PendingAction } from '../types';

interface ConfirmationModalProps {
  action: PendingAction | null;
  onConfirm: (actionId: string) => Promise<void>;
  onCancel: (actionId: string) => Promise<void>;
  isLoading: boolean;
}

export const ConfirmationModal: React.FC<ConfirmationModalProps> = ({ action, onConfirm, onCancel, isLoading }) => {
  if (!action) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-indigo-500/30 rounded-2xl max-w-lg w-full p-6 shadow-2xl shadow-indigo-500/10 animate-in fade-in zoom-in-95 duration-200">
        <div className="flex items-start gap-4">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0">
            <ShieldAlert className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
              Security Confirmation Required
            </span>
            <h3 className="text-lg font-bold text-slate-100 mt-1">Confirm Mutating Operation</h3>
            <p className="text-xs text-slate-400 mt-1">
              Under strict security requirements, AI-initiated write operations require your explicit authorization.
            </p>
          </div>
        </div>

        {/* Action Details */}
        <div className="my-5 p-4 rounded-xl bg-slate-950/80 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <GitBranch className="w-3.5 h-3.5 text-slate-400" />
            <span>Target:</span>
            <span className="font-mono text-indigo-300">
              {action.arguments.owner}/{action.arguments.repo}
            </span>
          </div>

          <div>
            <span className="text-xs text-slate-500 block mb-0.5">Issue Title:</span>
            <p className="text-sm font-semibold text-slate-200">{action.arguments.title}</p>
          </div>

          <div>
            <span className="text-xs text-slate-500 block mb-0.5">Issue Description:</span>
            <div className="max-h-40 overflow-y-auto bg-slate-900 p-2.5 rounded border border-slate-800 text-xs text-slate-300 whitespace-pre-wrap font-sans">
              {action.arguments.body}
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3">
          <button
            onClick={() => onCancel(action.action_id)}
            disabled={isLoading}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors cursor-pointer flex items-center gap-1.5"
          >
            <X className="w-3.5 h-3.5" />
            <span>Cancel</span>
          </button>

          <button
            onClick={() => onConfirm(action.action_id)}
            disabled={isLoading}
            className="px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold shadow-lg shadow-emerald-600/20 transition-all cursor-pointer flex items-center gap-1.5"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Creating Issue...</span>
              </>
            ) : (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Confirm & Create GitHub Issue</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
