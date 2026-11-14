import React, { useState } from 'react';
import {
  Play,
  ArrowRight,
  CheckCircle2,
  ShieldBan,
  AlertTriangle,
  Repeat,
  Info,
  Clock,
  Check,
  Sparkles,
  ShieldAlert,
} from 'lucide-react';
import { Workflow, WorkflowStep } from '../types';

interface WorkflowFlowchartProps {
  workflow: Workflow;
  onStepClick?: (stepNumber: number) => void;
}

export const WorkflowFlowchart: React.FC<WorkflowFlowchartProps> = ({
  workflow,
  onStepClick,
}) => {
  const [selectedStep, setSelectedStep] = useState<number | null>(null);

  const steps = workflow.steps || [];
  const hasLoop =
    workflow.status === 'BLOCKED' &&
    (workflow.termination_reason?.toLowerCase().includes('loop') ||
      steps.some((s) => s.rule_triggered?.includes('LOOP')));

  const getStepDescription = (step: WorkflowStep) => {
    if (step.safety_decision === 'BLOCK') {
      if (step.rule_triggered === 'INFINITE_LOOP_PREVENTION') {
        return '🚨 Infinite Loop Blocked: Repeating cyclic sequence detected before execution.';
      }
      if (step.rule_triggered === 'REPEATED_TOOL_CALL_DETECTED') {
        return '🛑 Repeated Calls Blocked: Identical tool call hash threshold exceeded.';
      }
      return `🛑 Blocked: Triggered safety rule [${step.rule_triggered || 'POLICY_VIOLATION'}].`;
    }
    if (step.safety_decision === 'REQUIRE_APPROVAL') {
      return `⚠️ Sensitive Tool [${step.tool_name}]: Safety gate paused workflow for human review.`;
    }
    return `✅ Allowed: Verified by all 5 deterministic safety gates (${step.duration_ms}ms).`;
  };

  return (
    <div className="glass-panel p-5 rounded-2xl border border-slate-800 space-y-4">
      {/* Graph Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 border-b border-slate-800/80 pb-3">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center">
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              Execution Flowchart & Pipeline Graph
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                Interactive Graph
              </span>
            </h3>
            <p className="text-[11px] text-slate-400">
              Student-friendly step progression showing pre-execution gate evaluation
            </p>
          </div>
        </div>

        {/* Legend for Students */}
        <div className="flex items-center gap-3 text-[11px] font-mono">
          <span className="flex items-center gap-1.5 text-emerald-400">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> ALLOW
          </span>
          <span className="flex items-center gap-1.5 text-rose-400">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500"></span> BLOCK
          </span>
          <span className="flex items-center gap-1.5 text-amber-400">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-500"></span> APPROVAL
          </span>
        </div>
      </div>

      {/* Cyclic Loop Banner if present */}
      {hasLoop && (
        <div className="p-3 rounded-xl bg-rose-950/20 border border-rose-500/30 flex items-center justify-between text-xs animate-pulse">
          <div className="flex items-center gap-2 text-rose-300">
            <Repeat className="w-4 h-4 text-rose-400" />
            <span className="font-semibold">Cyclic Loop Detected:</span>
            <span className="font-mono text-[11px] text-rose-200">
              Alternating pattern intercepted by Gate 4 (Sliding-Window N-gram)
            </span>
          </div>
          <span className="text-[10px] font-mono uppercase bg-rose-500/20 text-rose-300 px-2 py-0.5 rounded border border-rose-500/30">
            Cycle Threshold Reached
          </span>
        </div>
      )}

      {/* Flowchart Nodes Track */}
      <div className="overflow-x-auto py-4 px-2 scrollbar-thin">
        <div className="flex items-center gap-3 min-w-max">
          {/* Node 0: Start */}
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-xl bg-slate-900 border border-slate-700 flex flex-col items-center justify-center shadow-lg group hover:border-slate-500 transition">
              <Play className="w-5 h-5 text-indigo-400 fill-indigo-400/20" />
            </div>
            <span className="text-[11px] font-bold text-slate-300 mt-2 font-mono">START</span>
            <span className="text-[9px] text-slate-500">Task Init</span>
          </div>

          <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0" />

          {/* Step Nodes */}
          {steps.map((step, idx) => {
            const isBlocked = step.safety_decision === 'BLOCK' || step.status === 'BLOCKED';
            const isApproval = step.safety_decision === 'REQUIRE_APPROVAL';
            const isAllowed = step.safety_decision === 'ALLOW';
            const isSelected = selectedStep === step.step_number;

            return (
              <React.Fragment key={step.id || idx}>
                <div
                  onClick={() => {
                    setSelectedStep(isSelected ? null : step.step_number);
                    if (onStepClick) onStepClick(step.step_number);
                  }}
                  className={`cursor-pointer transition-all transform hover:-translate-y-1 ${
                    isSelected ? 'scale-105' : ''
                  }`}
                >
                  <div
                    className={`w-40 p-3 rounded-xl border flex flex-col justify-between shadow-lg relative ${
                      isBlocked
                        ? 'bg-rose-950/30 border-rose-500 shadow-rose-950/50'
                        : isApproval
                        ? 'bg-amber-950/30 border-amber-500 shadow-amber-950/50'
                        : 'bg-slate-900/90 border-emerald-500/50 hover:border-emerald-400'
                    }`}
                  >
                    {/* Top status header in card */}
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-[10px] font-mono px-1.5 py-0.5 rounded font-bold bg-slate-800 text-slate-300">
                        Step #{step.step_number}
                      </span>
                      {isBlocked ? (
                        <span className="w-5 h-5 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center">
                          <ShieldBan className="w-3.5 h-3.5" />
                        </span>
                      ) : isApproval ? (
                        <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 flex items-center justify-center">
                          <AlertTriangle className="w-3.5 h-3.5" />
                        </span>
                      ) : (
                        <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center">
                          <Check className="w-3.5 h-3.5" />
                        </span>
                      )}
                    </div>

                    {/* Tool Name */}
                    <div className="font-mono text-xs font-bold text-white truncate" title={step.tool_name}>
                      {step.tool_name}
                    </div>

                    {/* Decision pill */}
                    <div className="mt-2 flex items-center justify-between text-[10px]">
                      <span
                        className={`font-mono font-bold ${
                          isBlocked
                            ? 'text-rose-400'
                            : isApproval
                            ? 'text-amber-400'
                            : 'text-emerald-400'
                        }`}
                      >
                        {step.safety_decision}
                      </span>
                      <span className="text-slate-500 font-mono">{step.duration_ms}ms</span>
                    </div>

                    {/* Highlight ring if selected */}
                    {isSelected && (
                      <div className="absolute -inset-0.5 rounded-xl border-2 border-indigo-400 pointer-events-none animate-pulse" />
                    )}
                  </div>
                </div>

                <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
              </React.Fragment>
            );
          })}

          {/* Node Terminal: Final Status */}
          <div className="flex flex-col items-center">
            <div
              className={`w-12 h-12 rounded-xl border flex flex-col items-center justify-center shadow-lg ${
                workflow.status === 'COMPLETED'
                  ? 'bg-emerald-950/40 border-emerald-500'
                  : workflow.status === 'BLOCKED'
                  ? 'bg-rose-950/40 border-rose-500'
                  : workflow.status === 'PAUSED_APPROVAL'
                  ? 'bg-amber-950/40 border-amber-500'
                  : 'bg-slate-900 border-cyan-500 animate-pulse'
              }`}
            >
              {workflow.status === 'COMPLETED' ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400" />
              ) : workflow.status === 'BLOCKED' ? (
                <ShieldAlert className="w-6 h-6 text-rose-400" />
              ) : workflow.status === 'PAUSED_APPROVAL' ? (
                <Clock className="w-6 h-6 text-amber-400" />
              ) : (
                <Sparkles className="w-6 h-6 text-cyan-400" />
              )}
            </div>
            <span
              className={`text-[11px] font-bold mt-2 font-mono ${
                workflow.status === 'COMPLETED'
                  ? 'text-emerald-400'
                  : workflow.status === 'BLOCKED'
                  ? 'text-rose-400'
                  : workflow.status === 'PAUSED_APPROVAL'
                  ? 'text-amber-400'
                  : 'text-cyan-400'
              }`}
            >
              {workflow.status}
            </span>
            <span className="text-[9px] text-slate-500">Final Outcome</span>
          </div>
        </div>
      </div>

      {/* Selected Step Explainer Card for Students */}
      {selectedStep !== null && steps.find((s) => s.step_number === selectedStep) && (
        <div className="p-3.5 rounded-xl bg-slate-900/90 border border-indigo-500/30 text-xs animate-fadeIn space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Info className="w-4 h-4 text-indigo-400" />
              <span className="font-bold text-white">
                Student Explainer &mdash; Step #{selectedStep}:{' '}
                <span className="text-cyan-300 font-mono">
                  {steps.find((s) => s.step_number === selectedStep)?.tool_name}
                </span>
              </span>
            </div>
            <button
              onClick={() => setSelectedStep(null)}
              className="text-[10px] text-slate-400 hover:text-white"
            >
              ✕ Close
            </button>
          </div>
          <p className="text-slate-300">
            {getStepDescription(steps.find((s) => s.step_number === selectedStep)!)}
          </p>
          <div className="flex items-center gap-4 text-[10px] font-mono text-slate-400 pt-1 border-t border-slate-800">
            <span>
              Risk Level:{' '}
              <strong className="text-white">
                {steps.find((s) => s.step_number === selectedStep)?.risk_level || 'LOW'}
              </strong>
            </span>
            <span>
              Rule:{' '}
              <strong className="text-rose-300">
                {steps.find((s) => s.step_number === selectedStep)?.rule_triggered || 'None (Passed)'}
              </strong>
            </span>
            <span className="truncate max-w-xs">
              Hash:{' '}
              <span className="text-slate-400 font-mono">
                {steps.find((s) => s.step_number === selectedStep)?.normalized_hash?.slice(0, 16)}...
              </span>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};

