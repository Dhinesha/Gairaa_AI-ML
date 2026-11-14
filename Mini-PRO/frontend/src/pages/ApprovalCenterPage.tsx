import React, { useEffect, useState } from 'react';
import {
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  ExternalLink,
  ShieldAlert,
  UserCheck,
  Check,
  X,
} from 'lucide-react';
import { ApprovalRequest } from '../types';
import { api } from '../services/api';

interface ApprovalCenterPageProps {
  onSelectWorkflow: (id: string) => void;
  onRefreshApprovalsCount?: () => void;
}

export const ApprovalCenterPage: React.FC<ApprovalCenterPageProps> = ({
  onSelectWorkflow,
  onRefreshApprovalsCount,
}) => {
  const [approvals, setApprovals] = useState<ApprovalRequest[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeTab, setActiveTab] = useState<'PENDING' | 'HISTORY'>('PENDING');
  const [reviewerName, setReviewerName] = useState<string>('Sarah Jenkins (Lead Security Architect)');
  const [comments, setComments] = useState<Record<string, string>>({});
  const [processingId, setProcessingId] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<{ id: string; text: string; isError?: boolean } | null>(null);

  const fetchApprovals = async () => {
    try {
      setLoading(true);
      const data = await api.listApprovals();
      setApprovals(data);
      if (onRefreshApprovalsCount) onRefreshApprovalsCount();
    } catch (err) {
      console.error('Error fetching approvals:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
    const interval = setInterval(fetchApprovals, 4000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (approvalId: string) => {
    try {
      setProcessingId(approvalId);
      setActionMessage(null);
      const comment = comments[approvalId] || 'Authorized following safety evaluation review.';
      await api.approveAction(approvalId, reviewerName, comment);
      setActionMessage({ id: approvalId, text: 'Action successfully approved! Workflow is resuming execution.' });
      await fetchApprovals();
    } catch (err: any) {
      setActionMessage({
        id: approvalId,
        text: err.response?.data?.detail || 'Approval failed. Check backend authorization.',
        isError: true,
      });
    } finally {
      setProcessingId(null);
    }
  };

  const handleReject = async (approvalId: string) => {
    try {
      setProcessingId(approvalId);
      setActionMessage(null);
      const comment = comments[approvalId] || 'Rejected due to risk policy violation.';
      await api.rejectAction(approvalId, reviewerName, comment);
      setActionMessage({ id: approvalId, text: 'Action rejected. Workflow has been safely terminated.', isError: true });
      await fetchApprovals();
    } catch (err: any) {
      setActionMessage({
        id: approvalId,
        text: err.response?.data?.detail || 'Rejection failed.',
        isError: true,
      });
    } finally {
      setProcessingId(null);
    }
  };

  const pendingList = approvals.filter((a) => a.status === 'PENDING');
  const historyList = approvals.filter((a) => a.status !== 'PENDING');
  const currentList = activeTab === 'PENDING' ? pendingList : historyList;

  return (
    <div className="space-y-6 animate-fadeIn max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
            <CheckCircle2 className="w-6 h-6 text-amber-400" />
            Human-in-the-Loop Approval Center
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Review sensitive or destructive agent operations before they execute on external environments.
          </p>
        </div>
        <button
          id="refresh-approvals-btn"
          onClick={fetchApprovals}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-slate-700 bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium transition"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Reviewer Identity Selector */}
      <div className="glass-panel p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs">
        <div className="flex items-center gap-2">
          <UserCheck className="w-4 h-4 text-indigo-400" />
          <span className="text-slate-400">Authenticated Reviewer:</span>
          <span className="text-white font-semibold font-mono">{reviewerName}</span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold">
            AUTHORIZED ROLE: ADMIN
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            id="tab-pending-approvals"
            onClick={() => setActiveTab('PENDING')}
            className={`px-3 py-1.5 rounded-lg font-medium transition flex items-center gap-1.5 ${
              activeTab === 'PENDING'
                ? 'bg-amber-500 text-black font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900'
            }`}
          >
            Pending Queue
            {pendingList.length > 0 && (
              <span className="px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-black text-amber-400">
                {pendingList.length}
              </span>
            )}
          </button>
          <button
            id="tab-history-approvals"
            onClick={() => setActiveTab('HISTORY')}
            className={`px-3 py-1.5 rounded-lg font-medium transition ${
              activeTab === 'HISTORY'
                ? 'bg-indigo-600 text-white font-bold'
                : 'text-slate-400 hover:text-white bg-slate-900'
            }`}
          >
            Resolution History ({historyList.length})
          </button>
        </div>
      </div>

      {/* Approvals List */}
      <div className="space-y-4">
        {loading && approvals.length === 0 ? (
          <div className="glass-panel py-16 text-center text-slate-400 text-sm rounded-2xl border border-slate-800">
            Checking approval queue...
          </div>
        ) : currentList.length === 0 ? (
          <div className="glass-panel py-16 text-center text-slate-400 text-sm rounded-2xl border border-slate-800 space-y-2">
            <CheckCircle2 className="w-8 h-8 text-emerald-400 mx-auto opacity-70" />
            <p className="font-semibold text-slate-300">
              {activeTab === 'PENDING' ? 'All sensitive operations cleared!' : 'No resolution history found.'}
            </p>
            <p className="text-xs text-slate-500">
              {activeTab === 'PENDING' && 'When an agent attempts a sensitive tool call, it will appear here for sign-off.'}
            </p>
          </div>
        ) : (
          currentList.map((req) => (
            <div
              key={req.id}
              id={`approval-card-${req.id.substring(0, 8)}`}
              className={`glass-panel p-6 rounded-2xl border space-y-4 transition ${
                req.status === 'PENDING'
                  ? 'border-amber-500/40 bg-slate-900/70 shadow-glow-amber'
                  : req.status === 'APPROVED'
                  ? 'border-emerald-500/30 bg-emerald-950/10'
                  : 'border-rose-500/30 bg-rose-950/10'
              }`}
            >
              {/* Header */}
              <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase font-mono border ${
                    req.risk_level === 'CRITICAL' ? 'bg-rose-500/20 text-rose-400 border-rose-500/30' :
                    'bg-amber-500/20 text-amber-400 border-amber-500/30'
                  }`}>
                    {req.risk_level} RISK
                  </span>
                  <span className="font-mono text-base font-bold text-white">
                    {req.tool_name}
                  </span>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                    req.status === 'PENDING' ? 'bg-amber-500 text-black' :
                    req.status === 'APPROVED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                    'bg-rose-500/20 text-rose-400 border border-rose-500/30'
                  }`}>
                    {req.status}
                  </span>
                </div>

                <button
                  onClick={() => onSelectWorkflow(req.workflow_id)}
                  className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-mono"
                >
                  Workflow {req.workflow_id.substring(0, 8)}... <ExternalLink className="w-3 h-3" />
                </button>
              </div>

              {/* Justification & Reason */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-1">
                <span className="text-[10px] uppercase font-mono text-amber-400 font-semibold block">
                  Safety Gate Flag Reason:
                </span>
                <p className="leading-relaxed">{req.reason}</p>
              </div>

              {/* Proposed Arguments Preview */}
              <div>
                <div className="text-[10px] uppercase font-mono text-slate-500 mb-1">
                  Proposed Tool Arguments:
                </div>
                <pre className="p-3 rounded-xl bg-[#080C14] border border-slate-800 font-mono text-[11px] text-cyan-300 overflow-x-auto">
                  {JSON.stringify(req.tool_arguments || {}, null, 2)}
                </pre>
              </div>

              {/* Action Message feedback */}
              {actionMessage && actionMessage.id === req.id && (
                <div className={`p-3 rounded-lg text-xs font-semibold ${
                  actionMessage.isError ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                }`}>
                  {actionMessage.text}
                </div>
              )}

              {/* Reviewer Action Controls (for PENDING only) */}
              {req.status === 'PENDING' && (
                <div className="pt-3 border-t border-slate-800/80 flex flex-col sm:flex-row items-center gap-3">
                  <input
                    type="text"
                    id={`approval-comment-${req.id.substring(0, 8)}`}
                    placeholder="Enter review decision notes / compliance rationale..."
                    value={comments[req.id] || ''}
                    onChange={(e) => setComments({ ...comments, [req.id]: e.target.value })}
                    className="w-full sm:flex-1 px-3 py-2 rounded-xl bg-slate-800/80 border border-slate-700 text-white text-xs placeholder-slate-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
                  />
                  <div className="flex gap-2 w-full sm:w-auto justify-end">
                    <button
                      id={`reject-btn-${req.id.substring(0, 8)}`}
                      onClick={() => handleReject(req.id)}
                      disabled={processingId === req.id}
                      className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-rose-600/20 hover:bg-rose-600/30 text-rose-300 border border-rose-500/30 font-semibold text-xs transition disabled:opacity-50"
                    >
                      <X className="w-3.5 h-3.5" /> Reject Action
                    </button>
                    <button
                      id={`approve-btn-${req.id.substring(0, 8)}`}
                      onClick={() => handleApprove(req.id)}
                      disabled={processingId === req.id}
                      className="flex items-center gap-1.5 px-5 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition disabled:opacity-50"
                    >
                      <Check className="w-3.5 h-3.5" /> Approve & Resume
                    </button>
                  </div>
                </div>
              )}

              {/* Past Reviewer Info */}
              {req.status !== 'PENDING' && (
                <div className="pt-2 border-t border-slate-800/80 text-[11px] text-slate-400 flex items-center justify-between font-mono">
                  <span>Reviewed by: <strong className="text-white">{req.reviewed_by}</strong></span>
                  <span>Decision: <strong className={req.status === 'APPROVED' ? 'text-emerald-400' : 'text-rose-400'}>{req.status}</strong></span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
