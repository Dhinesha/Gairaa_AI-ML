import React, { useEffect, useState } from 'react';
import {
  ArrowLeft,
  Square,
  Play,
  Pause,
  RotateCcw,
  CheckCircle2,
  AlertOctagon,
  Clock,
  Layers,
  ChevronDown,
  ChevronRight,
  ShieldAlert,
  AlertTriangle,
  FileCode,
  Terminal,
  Activity,
  Download,
  Printer,
  FileJson,
  Languages,
  Sparkles,
  BookOpen,
  Repeat,
  ShieldCheck,
  HelpCircle,
  Volume2,
  VolumeX,
} from 'lucide-react';
import { Workflow, WorkflowStep } from '../types';
import { api } from '../services/api';
import { WorkflowFlowchart } from '../components/WorkflowFlowchart';

interface StepExplanation {
  gateName: string;
  gateBadge: string;
  phaseLabel: string;
  englishSummary: string;
  tamilSummary: string;
  technicalReason: string;
}

const getStepExplanation = (
  step: WorkflowStep,
  allSteps: WorkflowStep[],
  workflow: Workflow
): StepExplanation => {
  const stepNum = step.step_number;
  const tool = step.tool_name;
  const isBlocked = step.safety_decision === 'BLOCK' || step.status === 'BLOCKED';
  const isApproval = step.safety_decision === 'REQUIRE_APPROVAL';
  const rule = step.rule_triggered || '';
  const isCyclicScenario =
    workflow.agent_type?.includes('infinite_loop') ||
    workflow.task?.toLowerCase().includes('synchronization') ||
    (allSteps.length >= 2 && (tool === 'tool_a' || tool === 'tool_b'));

  // 1. BLOCKED Cases
  if (isBlocked) {
    if (rule.includes('INFINITE_LOOP') || isCyclicScenario) {
      return {
        gateName: 'Gate #4 — Sliding-Window N-Gram Loop Detector',
        gateBadge: 'Gate 4 • Loop Breaker',
        phaseLabel: `Cycle ${Math.max(2, Math.floor(stepNum / 2))} • Loop Tripped`,
        englishSummary:
          '2 complete alternating cycles of [tool_a -> tool_b] detected with zero state progression. Intercepted and BLOCKED before execution to prevent runaway loop and compute cost.',
        tamilSummary:
          'ஒரே மாதிரியான 2 முழு சுழற்சிகள் (tool_a -> tool_b) எந்த முன்னேற்றமும் இல்லாமல் முடிந்தது உறுதியானதால், Pre-execution நிலையிலேயே BLOCK செய்து முடிவில்லாத சுழற்சி தடுத்து நிறுத்தப்பட்டது.',
        technicalReason:
          'Sliding-window pattern sequence [tool_a, tool_b, tool_a, tool_b] matched period K=2 threshold (2 cycles). Tool was not executed.',
      };
    }

    if (rule.includes('REPEATED_TOOL_CALL') || rule.includes('REPEAT')) {
      return {
        gateName: 'Gate #3 — Repeated Tool-Call Gate',
        gateBadge: 'Gate 3 • Repeat Gate',
        phaseLabel: 'Duplicate Hash Threshold Exceeded',
        englishSummary:
          `Consecutive repeated call to [${tool}] with equivalent normalized SHA-256 argument hash. Blocked to prevent redundant API queries.`,
        tamilSummary:
          `ஒரே டூல் [${tool}] அதே ஆர்கியூமென்ட்களுடன் மீண்டும் மீண்டும் அழைக்கப்பட்டதால், SHA-256 hash சரிபார்க்கப்பட்டு தடுத்து நிறுத்தப்பட்டது.`,
        technicalReason:
          'SHA-256 canonical argument hash matched consecutive history exceeding repeated call budget.',
      };
    }

    if (rule.includes('NO_PROGRESS') || rule.includes('STAGNATION')) {
      return {
        gateName: 'Gate #5 — No-Progress Entropy Stagnation Gate',
        gateBadge: 'Gate 5 • Stagnation Gate',
        phaseLabel: 'Zero Entropy Delta',
        englishSummary:
          'Agent repeatedly returned static payloads with zero informational entropy gain. Blocked to avoid wasted LLM tokens.',
        tamilSummary:
          'எந்தவித முன்னேற்றமும் இல்லாத static payload தொடர்ந்து வந்ததால், API டோக்கன் வீணாவதை தடுக்க இந்த டூல் Pre-execution நிலையில் நிறுத்தப்பட்டது.',
        technicalReason:
          'Output entropy delta <= 0.0 across consecutive steps with no new data discovered.',
      };
    }

    if (rule.includes('BUDGET') || rule.includes('TIMEOUT') || rule.includes('STEP_LIMIT')) {
      return {
        gateName: 'Gate #1 — Execution Budget Enforcement Gate',
        gateBadge: 'Gate 1 • Budget Gate',
        phaseLabel: 'Execution Budget Exceeded',
        englishSummary:
          'Workflow exceeded allocated step budget or maximum timeout. Blocked safely by supervisor.',
        tamilSummary:
          'அனுமதிக்கப்பட்ட அதிகபட்ச படிகள் அல்லது கால அவகாசத்தை தாண்டியதால் பாதுகாப்பாக நிறுத்தப்பட்டது.',
        technicalReason:
          'Workflow bounded budget enforcement halted runaway execution.',
      };
    }

    return {
      gateName: 'Deterministic Safety Supervisor',
      gateBadge: 'Safety Gate',
      phaseLabel: 'Policy Violation Block',
      englishSummary: `Action blocked by runtime safety gate [${rule || 'POLICY_GUARD'}].`,
      tamilSummary: `பாதுகாப்பு விதி [${rule || 'POLICY_GUARD'}] தூண்டப்பட்டு இந்த செயல் தடுத்து நிறுத்தப்பட்டது.`,
      technicalReason: `Rule ${rule} triggered block policy.`,
    };
  }

  // 2. REQUIRE_APPROVAL Cases
  if (isApproval) {
    return {
      gateName: 'Gate #2 — Risk-Based Policy Gate',
      gateBadge: 'Gate 2 • Human in the Loop',
      phaseLabel: 'Sensitive Mutation Gated',
      englishSummary:
        `High-risk action [${tool}] detected (e.g. salary adjustment, system write). Workflow paused awaiting authorized Human Approval sign-off.`,
      tamilSummary:
        `உயர் பாதுகாப்பு தேவைப்படும் செயல் [${tool}] (Salary/HR மாற்றம்) கண்டறியப்பட்டதால், மனித ஒப்புதலுக்காக (Human Approval) தற்காலிகமாக நிறுத்தப்பட்டுள்ளது.`,
      technicalReason:
        'Sensitive tool regex matched. Routed to Human-in-the-Loop authorization queue in Approval Center.',
    };
  }

  // 3. ALLOW Cases
  if (isCyclicScenario) {
    if (stepNum === 1) {
      return {
        gateName: 'Gate #4 — Sliding-Window Loop Detector (Baseline)',
        gateBadge: 'Gate 4 • Exploration',
        phaseLabel: 'Cycle 1 • Phase 1/2: Initial Feed Lookup',
        englishSummary:
          'Initial exploratory invocation of tool_a. Allowed as safety engine builds the baseline execution history buffer.',
        tamilSummary:
          'முதல் முறை தரவு சேகரிப்புக்கான அழைப்பு (tool_a) என்பதால், Engine எவ்வித தடையுமின்றி அனுமதித்துள்ளது (ALLOW).',
        technicalReason:
          'Baseline call with no prior history. SHA-256 hash registered in sliding-window history buffer.',
      };
    }
    if (stepNum === 2) {
      return {
        gateName: 'Gate #4 — Sliding-Window Loop Detector (Sequence Building)',
        gateBadge: 'Gate 4 • Progression',
        phaseLabel: 'Cycle 1 • Phase 2/2: Cache Sync',
        englishSummary:
          'Agent invokes tool_b to synchronize cache. Allowed as a valid progression; candidate 2-gram [tool_a, tool_b] is formed.',
        tamilSummary:
          'tool_a-வில் இருந்து மாறுபட்ட புதிய செயல் (tool_b) என்பதால் அடுத்தகட்ட பணிக்காக அனுமதிக்கப்பட்டது (ALLOW).',
        technicalReason:
          'Different tool name and arguments. Candidate N-gram sequence of period K=2 created in memory.',
      };
    }
    if (stepNum === 3) {
      return {
        gateName: 'Gate #4 — Sliding-Window Loop Detector (Monitoring)',
        gateBadge: 'Gate 4 • Monitoring',
        phaseLabel: 'Cycle 2 • Phase 1/2: Sequence Re-invocation',
        englishSummary:
          'tool_a is invoked again after tool_b. Allowed under threshold to permit legitimate data refreshes; loop cycle counter incremented to 1.5.',
        tamilSummary:
          'tool_a மீண்டும் அழைக்கப்படுகிறது. தற்காலிகமாக அனுமதிக்கப்பட்டு, சுழற்சி கவுண்டர் (Cycle=1.5) உயர்த்தப்பட்டது.',
        technicalReason:
          'Sequence [tool_a, tool_b, tool_a] detected. 1 full cycle completed; threshold is 2 full cycles before hard block.',
      };
    }
  }

  // Standard Allowed Steps
  return {
    gateName: 'Gates 1 to 5: Deterministic Policy Supervisor',
    gateBadge: 'Verified Safe',
    phaseLabel: `Step ${stepNum} Progression Clear`,
    englishSummary:
      `Action [${tool}] validated across all 5 safety gates. No loops, duplicate hashes, or sensitive permission violations detected.`,
    tamilSummary:
      `அனைத்து 5 பாதுகாப்பு சோதனைகளையும் கடந்து, எவ்வித சுழற்சி அல்லது விதிமீறலும் இல்லாததால் அனுமதிக்கப்பட்டது (ALLOW).`,
    technicalReason:
      'Execution step budget, argument hash novelty, and sensitive regex checks all passed clear.',
  };
};

interface WorkflowDetailsPageProps {
  workflowId: string;
  onBack: () => void;
  onGoToApprovals: () => void;
}

export const WorkflowDetailsPage: React.FC<WorkflowDetailsPageProps> = ({
  workflowId,
  onBack,
  onGoToApprovals,
}) => {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [actionLoading, setActionLoading] = useState<boolean>(false);
  const [expandedSteps, setExpandedSteps] = useState<Record<number, boolean>>({});
  const [summaryLang, setSummaryLang] = useState<'both' | 'en' | 'ta'>('both');

  // Voice Translator & Speech Synthesis State
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false);
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const [speakingStepNum, setSpeakingStepNum] = useState<number | null>(null);
  const [speechRate, setSpeechRate] = useState<number>(0.95);
  const speakingStepIndexRef = React.useRef<number>(0);

  const stopVoice = () => {
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
    setIsPaused(false);
    setSpeakingStepNum(null);
  };

  useEffect(() => {
    return () => {
      stopVoice();
    };
  }, []);

  const speakStepSequence = (index: number, stepsList: WorkflowStep[]) => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
      alert('Text-to-speech voice narration is not supported in this browser.');
      return;
    }
    if (index >= stepsList.length) {
      setIsSpeaking(false);
      setSpeakingStepNum(null);
      return;
    }

    speakingStepIndexRef.current = index;
    const currentStep = stepsList[index];
    setSpeakingStepNum(currentStep.step_number);
    setIsSpeaking(true);
    setIsPaused(false);

    const exp = getStepExplanation(currentStep, workflow?.steps || [], workflow!);

    let script = '';
    if (summaryLang === 'ta') {
      script = `படி ${currentStep.step_number}. டூல் ${currentStep.tool_name}. ${exp.tamilSummary}`;
    } else if (summaryLang === 'en') {
      script = `Step ${currentStep.step_number}. Tool ${currentStep.tool_name}. Safety decision: ${currentStep.safety_decision}. ${exp.englishSummary}`;
    } else {
      // Both (Bilingual voice breakdown)
      script = `Step ${currentStep.step_number}: Tool ${currentStep.tool_name}. ${exp.englishSummary}. தமிழில்: ${exp.tamilSummary}`;
    }

    const utterance = new SpeechSynthesisUtterance(script);
    utterance.rate = speechRate;
    utterance.pitch = 1.0;

    const voices = window.speechSynthesis.getVoices();
    if (summaryLang === 'ta') {
      const taVoice = voices.find(
        (v) => v.lang.startsWith('ta') || v.name.toLowerCase().includes('tamil')
      );
      if (taVoice) {
        utterance.voice = taVoice;
        utterance.lang = 'ta-IN';
      } else {
        utterance.lang = 'en-IN';
      }
    } else {
      const enVoice = voices.find(
        (v) =>
          v.lang.startsWith('en') &&
          (v.name.includes('Natural') ||
            v.name.includes('Google') ||
            v.name.includes('Microsoft') ||
            v.name.includes('Samantha') ||
            v.default)
      );
      if (enVoice) {
        utterance.voice = enVoice;
      }
      utterance.lang = 'en-US';
    }

    utterance.onend = () => {
      setTimeout(() => {
        if (speakingStepIndexRef.current === index) {
          speakStepSequence(index + 1, stepsList);
        }
      }, 450);
    };

    utterance.onerror = (e) => {
      if (e.error !== 'canceled') {
        console.warn('Speech error:', e);
      }
      setIsSpeaking(false);
      setSpeakingStepNum(null);
    };

    window.speechSynthesis.speak(utterance);
  };

  const handleToggleVoiceAll = () => {
    if (!workflow?.steps || workflow.steps.length === 0) return;
    if (isSpeaking) {
      stopVoice();
    } else {
      stopVoice();
      speakStepSequence(0, workflow.steps);
    }
  };

  const handleSpeakSingleStep = (step: WorkflowStep) => {
    stopVoice();
    speakStepSequence(0, [step]);
  };

  const handlePauseResumeVoice = () => {
    if (typeof window === 'undefined' || !('speechSynthesis' in window)) return;
    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume();
      setIsPaused(false);
    } else if (window.speechSynthesis.speaking) {
      window.speechSynthesis.pause();
      setIsPaused(true);
    }
  };

  const fetchDetails = async () => {
    try {
      const data = await api.getWorkflow(workflowId);
      setWorkflow(data);
      // Auto expand latest step
      if (data.steps && data.steps.length > 0) {
        const latestStepNum = data.steps[data.steps.length - 1].step_number;
        setExpandedSteps((prev) => ({ ...prev, [latestStepNum]: true }));
      }
    } catch (err) {
      console.error('Error fetching workflow details:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
    // Live polling every 1.5s while RUNNING or PENDING
    const interval = setInterval(() => {
      if (workflow?.status === 'RUNNING' || workflow?.status === 'PENDING') {
        fetchDetails();
      }
    }, 1500);
    return () => clearInterval(interval);
  }, [workflowId, workflow?.status]);

  const toggleStep = (stepNum: number) => {
    setExpandedSteps((prev) => ({
      ...prev,
      [stepNum]: !prev[stepNum],
    }));
  };

  const handleStop = async () => {
    try {
      setActionLoading(true);
      await api.stopWorkflow(workflowId);
      await fetchDetails();
    } catch (err) {
      console.error('Stop error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResume = async () => {
    try {
      setActionLoading(true);
      await api.resumeWorkflow(workflowId);
      await fetchDetails();
    } catch (err) {
      console.error('Resume error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleRetry = async () => {
    try {
      setActionLoading(true);
      await api.retryWorkflow(workflowId);
      await fetchDetails();
    } catch (err) {
      console.error('Retry error:', err);
    } finally {
      setActionLoading(false);
    }
  };

  const handleDownloadJSON = () => {
    if (!workflow) return;
    const exportData = {
      project: "Agent Workflow Safety & Loop Prevention Engine (LoopGuard)",
      report_generated_at: new Date().toISOString(),
      workflow_id: workflow.id,
      task_instruction: workflow.task,
      agent_type: workflow.agent_type,
      status: workflow.status,
      execution_duration_seconds: workflow.execution_duration_seconds,
      total_steps: workflow.step_count,
      termination_reason: workflow.termination_reason || null,
      result_summary: workflow.result_summary || null,
      steps_trace: (workflow.steps || []).map((s) => ({
        step_number: s.step_number,
        tool_name: s.tool_name,
        safety_decision: s.safety_decision,
        rule_triggered: s.rule_triggered || null,
        risk_level: s.risk_level,
        duration_ms: s.duration_ms,
        normalized_hash: s.normalized_hash,
        sanitized_arguments: s.sanitized_arguments || s.raw_arguments,
        tool_result: s.tool_result,
        timestamp: s.timestamp,
      })),
      safety_events: workflow.events || [],
      approvals: workflow.approvals || [],
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `loopguard_audit_${workflow.id.slice(0, 8)}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const handlePrintReport = () => {
    window.print();
  };

  const getDecisionBadge = (decision: string) => {
    switch (decision) {
      case 'ALLOW':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            ALLOW
          </span>
        );
      case 'BLOCK':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-rose-500/10 text-rose-400 border border-rose-500/20">
            BLOCK
          </span>
        );
      case 'REQUIRE_APPROVAL':
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-mono font-bold bg-amber-500/10 text-amber-400 border border-amber-500/20 animate-pulse">
            REQUIRE_APPROVAL
          </span>
        );
      default:
        return <span className="text-slate-400">{decision}</span>;
    }
  };

  if (loading && !workflow) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-slate-400 space-y-3">
        <div className="w-8 h-8 border-2 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin" />
        <span className="text-sm">Loading execution details...</span>
      </div>
    );
  }

  if (!workflow) {
    return (
      <div className="text-center py-20 text-slate-400">
        <p>Workflow not found.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 rounded-lg bg-slate-800 text-xs">
          Return to List
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fadeIn pb-12">
      {/* Top Bar Navigation */}
      <div className="flex items-center justify-between">
        <button
          id="back-to-workflows-btn"
          onClick={onBack}
          className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition"
        >
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <div className="flex items-center gap-2">
          {workflow.status === 'RUNNING' && (
            <button
              id="stop-workflow-btn"
              onClick={handleStop}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-rose-600/20 hover:bg-rose-600/30 border border-rose-500/30 text-rose-300 text-xs font-semibold transition"
            >
              <Square className="w-3.5 h-3.5 fill-rose-300" /> Stop Execution
            </button>
          )}

          {(workflow.status === 'BLOCKED' || workflow.status === 'STOPPED') && (
            <button
              id="retry-workflow-btn"
              onClick={handleRetry}
              disabled={actionLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition"
            >
              <RotateCcw className="w-3.5 h-3.5" /> Retry Execution
            </button>
          )}

          {workflow.status === 'PAUSED_APPROVAL' && (
            <button
              id="go-to-approval-btn"
              onClick={onGoToApprovals}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-400 text-black text-xs font-bold shadow-md shadow-amber-500/20 transition animate-bounce"
            >
              <AlertTriangle className="w-4 h-4" /> Open Approval Center
            </button>
          )}

          {/* Download & Export Action Buttons */}
          <button
            id="download-json-report-btn"
            onClick={handleDownloadJSON}
            title="Download full audit report as JSON file"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium transition shadow-sm"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden sm:inline">Export JSON</span>
          </button>

          <button
            id="print-report-btn"
            onClick={handlePrintReport}
            title="Print or Save as PDF Report for submission"
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium transition shadow-sm"
          >
            <Printer className="w-3.5 h-3.5 text-cyan-400" />
            <span className="hidden sm:inline">Print / PDF</span>
          </button>
        </div>
      </div>

      {/* Main Workflow Header Card */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="text-xs font-mono text-slate-400">Workflow ID:</span>
              <span className="font-mono text-xs font-semibold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
                {workflow.id}
              </span>
              <span className={`px-2.5 py-0.5 rounded text-xs font-bold ${
                workflow.status === 'COMPLETED' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' :
                workflow.status === 'BLOCKED' ? 'bg-rose-500/20 text-rose-400 border border-rose-500/30' :
                workflow.status === 'PAUSED_APPROVAL' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' :
                workflow.status === 'RUNNING' ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 animate-pulse' :
                'bg-slate-800 text-slate-300'
              }`}>
                {workflow.status}
              </span>
            </div>
            <h1 className="text-lg font-bold text-white tracking-tight">{workflow.task}</h1>
          </div>
          <div className="flex items-center gap-4 text-xs font-mono text-slate-400 bg-slate-900/60 p-2 rounded-xl border border-slate-800">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Agent</span>
              <span className="text-slate-200 font-semibold">{workflow.agent_type}</span>
            </div>
            <div className="border-l border-slate-800 pl-4">
              <span className="text-slate-500 block text-[10px] uppercase">Steps</span>
              <span className="text-slate-200 font-semibold">{workflow.step_count}</span>
            </div>
            <div className="border-l border-slate-800 pl-4">
              <span className="text-slate-500 block text-[10px] uppercase">Duration</span>
              <span className="text-slate-200 font-semibold">{workflow.execution_duration_seconds}s</span>
            </div>
          </div>
        </div>

        {/* Termination Reason Alert Banner */}
        {workflow.termination_reason && (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-200 text-xs flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-bold text-rose-400 mb-0.5 uppercase tracking-wider text-[11px]">
                Safety Gate Interception &mdash; Execution Terminated
              </div>
              <p className="leading-relaxed">{workflow.termination_reason}</p>
            </div>
          </div>
        )}

        {/* Completion Result Box */}
        {workflow.result_summary && (
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-200 text-xs flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-bold text-emerald-400 mb-0.5 uppercase tracking-wider text-[11px]">
                Workflow Successfully Achieved
              </div>
              <p className="leading-relaxed">{workflow.result_summary}</p>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Execution Flowchart Graph for Students */}
      {workflow.steps && workflow.steps.length > 0 && (
        <WorkflowFlowchart
          workflow={workflow}
          onStepClick={(stepNum) => {
            setExpandedSteps((prev) => ({ ...prev, [stepNum]: true }));
            const element = document.getElementById(`step-card-${stepNum}`);
            if (element) {
              element.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
          }}
        />
      )}

      {/* Executive Step-by-Step Summary Table (Student & Viva Mode) */}
      {workflow.steps && workflow.steps.length > 0 && (
        <div className="glass-panel p-5 rounded-2xl border border-indigo-500/30 bg-slate-950/70 space-y-4">
          <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-3 border-b border-slate-800/80 pb-3">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
                <BookOpen className="w-4 h-4 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  Executive Step-by-Step Analysis & Safety Gate Summary
                </h3>
                <p className="text-[11px] text-slate-400">
                  Comprehensive breakdown of each execution step, safety gate evaluation, and termination logic
                </p>
              </div>
            </div>

            {/* Language Selector + Voice Translator (Placed to the right below arrow mark) */}
            <div className="flex items-center gap-2 flex-wrap sm:flex-nowrap flex-shrink-0">
              {/* Language Selector */}
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono shadow-sm">
                <Languages className="w-3.5 h-3.5 text-cyan-400 ml-1.5 mr-0.5" />
                <button
                  type="button"
                  onClick={() => { stopVoice(); setSummaryLang('both'); }}
                  className={`px-2.5 py-1 rounded-lg transition ${
                    summaryLang === 'both'
                      ? 'bg-indigo-600 text-white font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🌐 Both (Bilingual)
                </button>
                <button
                  type="button"
                  onClick={() => { stopVoice(); setSummaryLang('en'); }}
                  className={`px-2.5 py-1 rounded-lg transition ${
                    summaryLang === 'en'
                      ? 'bg-indigo-600 text-white font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇺🇸 English
                </button>
                <button
                  type="button"
                  onClick={() => { stopVoice(); setSummaryLang('ta'); }}
                  className={`px-2.5 py-1 rounded-lg transition ${
                    summaryLang === 'ta'
                      ? 'bg-indigo-600 text-white font-bold shadow-sm'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  🇮🇳 தமிழ்
                </button>
              </div>

              {/* Voice Translator (Relocated below arrow mark, to the right of language selector) */}
              <div className="flex items-center gap-1.5 p-1 rounded-xl bg-slate-900 border border-slate-800 text-[11px] font-mono shadow-sm">
                <button
                  type="button"
                  id="voice-narrator-btn"
                  onClick={handleToggleVoiceAll}
                  className={`flex items-center gap-1.5 px-3 py-1 rounded-lg transition font-medium whitespace-nowrap ${
                    isSpeaking
                      ? 'bg-emerald-600 text-white shadow-sm shadow-emerald-500/30'
                      : 'bg-indigo-600/20 hover:bg-indigo-600 text-indigo-300 hover:text-white border border-indigo-500/30'
                  }`}
                  title={isSpeaking ? 'Stop Voice Narration' : 'Listen to Step-by-Step Voice Explanation'}
                >
                  <Volume2 className={`w-3.5 h-3.5 ${isSpeaking ? 'animate-bounce text-white' : 'text-cyan-400'}`} />
                  <span>{isSpeaking ? (speakingStepNum ? `Speaking #${speakingStepNum}...` : 'Speaking...') : 'Voice Translator'}</span>
                  {isSpeaking && (
                    <span className="flex items-center gap-0.5 ml-1">
                      <span className="w-0.5 h-2.5 bg-white rounded-full animate-pulse" />
                      <span className="w-0.5 h-3.5 bg-white rounded-full animate-pulse [animation-delay:0.15s]" />
                      <span className="w-0.5 h-2 bg-white rounded-full animate-pulse [animation-delay:0.3s]" />
                    </span>
                  )}
                </button>

                {isSpeaking && (
                  <>
                    <button
                      type="button"
                      onClick={handlePauseResumeVoice}
                      className="p-1 px-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition"
                      title={isPaused ? 'Resume Voice' : 'Pause Voice'}
                    >
                      {isPaused ? <Play className="w-3.5 h-3.5 text-emerald-400" /> : <Pause className="w-3.5 h-3.5 text-amber-400" />}
                    </button>

                    <button
                      type="button"
                      onClick={stopVoice}
                      className="p-1 px-1.5 rounded-lg text-rose-400 hover:text-rose-300 hover:bg-slate-800 transition"
                      title="Stop Voice Narration"
                    >
                      <Square className="w-3.5 h-3.5" />
                    </button>
                  </>
                )}

                {/* Speed Rate Toggle */}
                <button
                  type="button"
                  onClick={() => setSpeechRate((r) => (r === 0.95 ? 1.2 : r === 1.2 ? 0.8 : 0.95))}
                  className="px-1.5 py-0.5 rounded text-[10px] text-slate-400 hover:text-slate-200 hover:bg-slate-800 border border-slate-700/60 transition whitespace-nowrap"
                  title="Playback Speech Speed"
                >
                  {speechRate === 0.95 ? '1x' : `${speechRate}x`}
                </button>
              </div>
            </div>
          </div>

          {/* Summary Table */}
          <div className="overflow-x-auto rounded-xl border border-slate-800/80">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-slate-900/90 text-slate-400 border-b border-slate-800 uppercase text-[10px]">
                <tr>
                  <th className="py-2.5 px-3">Step</th>
                  <th className="py-2.5 px-3">Tool & Phase</th>
                  <th className="py-2.5 px-3">Gate Evaluated</th>
                  <th className="py-2.5 px-3">Decision</th>
                  <th className="py-2.5 px-4">Summary & Reason (விளக்கம்)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                {workflow.steps.map((st) => {
                  const exp = getStepExplanation(st, workflow.steps || [], workflow);

                  return (
                    <tr
                      key={st.id}
                      onClick={() => {
                        toggleStep(st.step_number);
                        const el = document.getElementById(`step-card-${st.step_number}`);
                        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' });
                      }}
                      className={`transition cursor-pointer ${
                        speakingStepNum === st.step_number
                          ? 'bg-indigo-950/60 ring-1 ring-cyan-400/50'
                          : 'hover:bg-slate-900/60'
                      }`}
                    >
                      <td className="py-3 px-3 font-bold text-white whitespace-nowrap">
                        <div className="flex items-center gap-1.5">
                          <span>#{st.step_number}</span>
                          <button
                            type="button"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleSpeakSingleStep(st);
                            }}
                            className={`p-1 rounded-md transition ${
                              speakingStepNum === st.step_number
                                ? 'bg-cyan-500/20 text-cyan-400 ring-1 ring-cyan-400/50'
                                : 'hover:bg-slate-800 text-slate-400 hover:text-cyan-300'
                            }`}
                            title={`Listen to Step #${st.step_number} Audio Explanation`}
                          >
                            <Volume2
                              className={`w-3.5 h-3.5 ${
                                speakingStepNum === st.step_number ? 'animate-bounce text-cyan-400' : ''
                              }`}
                            />
                          </button>
                        </div>
                      </td>
                      <td className="py-3 px-3">
                        <span className="font-bold text-cyan-300 block">{st.tool_name}</span>
                        <span className="text-[10px] text-slate-400">{exp.phaseLabel}</span>
                      </td>
                      <td className="py-3 px-3">
                        <span className="text-slate-300 text-[11px] block">{exp.gateName}</span>
                      </td>
                      <td className="py-3 px-3 whitespace-nowrap">
                        {getDecisionBadge(st.safety_decision)}
                      </td>
                      <td className="py-3 px-4 font-sans text-xs">
                        {(summaryLang === 'en' || summaryLang === 'both') && (
                          <p className="text-slate-200 leading-relaxed mb-1 font-mono text-[11px]">
                            {exp.englishSummary}
                          </p>
                        )}
                        {(summaryLang === 'ta' || summaryLang === 'both') && (
                          <p className="text-cyan-300/90 leading-relaxed text-[11px]">
                            {exp.tamilSummary}
                          </p>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Ordered Execution Steps */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" /> Ordered Execution Trace & Safety Decisions
          </h2>
          <span className="text-xs text-slate-500 font-mono">
            {workflow.steps?.length ?? 0} Steps Logged
          </span>
        </div>

        {!workflow.steps || workflow.steps.length === 0 ? (
          <div className="glass-panel p-10 rounded-2xl border border-slate-800 text-center text-slate-500 text-xs">
            {workflow.status === 'RUNNING' ? 'Agent analyzing task and preparing proposed tool invocation...' : 'No execution steps recorded.'}
          </div>
        ) : (
          <div className="space-y-3">
            {workflow.steps.map((step) => {
              const isExpanded = expandedSteps[step.step_number];
              const isBlocked = step.safety_decision === 'BLOCK' || step.status === 'BLOCKED';
              const isApproval = step.safety_decision === 'REQUIRE_APPROVAL';

              return (
                <div
                  key={step.id}
                  id={`step-card-${step.step_number}`}
                  className={`rounded-2xl border transition overflow-hidden ${
                    isBlocked
                      ? 'border-rose-500/40 bg-rose-950/10'
                      : isApproval
                      ? 'border-amber-500/40 bg-amber-950/10'
                      : 'border-slate-800/80 bg-slate-900/50 hover:border-slate-700'
                  }`}
                >
                  {/* Step Header */}
                  <div
                    onClick={() => toggleStep(step.step_number)}
                    className="p-4 flex items-center justify-between cursor-pointer select-none"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center font-mono text-xs font-bold ${
                        isBlocked
                          ? 'bg-rose-500/20 text-rose-400'
                          : isApproval
                          ? 'bg-amber-500/20 text-amber-400'
                          : 'bg-indigo-500/20 text-indigo-400'
                      }`}>
                        {step.step_number}
                      </div>

                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-semibold text-white">
                            {step.tool_name}
                          </span>
                          {getDecisionBadge(step.safety_decision)}
                          {step.risk_level && step.risk_level !== 'LOW' && (
                            <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20">
                              {step.risk_level}
                            </span>
                          )}
                        </div>
                        {step.rule_triggered && (
                          <div className="text-[11px] text-rose-400 font-mono mt-0.5">
                            Rule: {step.rule_triggered}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="flex items-center gap-3 text-xs font-mono text-slate-400">
                      <span>{step.duration_ms}ms</span>
                      {isExpanded ? (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronRight className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                  </div>

                  {/* Expanded Step Body */}
                  {isExpanded && (
                    <div className="px-4 pb-4 pt-1 border-t border-slate-800/60 space-y-3 text-xs animate-fadeIn">
                      {/* Step Safety Analysis & Reason Card */}
                      {(() => {
                        const exp = getStepExplanation(step, workflow.steps || [], workflow);
                        return (
                          <div className="p-3.5 rounded-xl bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 border border-cyan-500/30 space-y-2 mt-2">
                            <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-800/80 pb-2 text-[11px] font-mono">
                              <div className="flex items-center gap-2">
                                <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
                                <span className="font-bold text-white">Step Safety Analysis:</span>
                                <span className="text-cyan-300 font-semibold">{exp.gateName}</span>
                              </div>
                              <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 text-[10px]">
                                {exp.phaseLabel}
                              </span>
                            </div>

                            <div className="space-y-1.5 text-xs">
                              {(summaryLang === 'en' || summaryLang === 'both') && (
                                <div className="flex items-start gap-2">
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300 font-bold flex-shrink-0 mt-0.5">
                                    EN
                                  </span>
                                  <p className="text-slate-200 leading-relaxed font-mono text-[11px]">{exp.englishSummary}</p>
                                </div>
                              )}

                              {(summaryLang === 'ta' || summaryLang === 'both') && (
                                <div className="flex items-start gap-2">
                                  <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-cyan-400 font-bold flex-shrink-0 mt-0.5">
                                    தமிழ்
                                  </span>
                                  <p className="text-cyan-300 leading-relaxed font-sans text-xs">{exp.tamilSummary}</p>
                                </div>
                              )}
                            </div>

                            <div className="pt-1.5 border-t border-slate-800/60 text-[10px] font-mono text-slate-400 flex flex-wrap items-center justify-between gap-2">
                              <span>Technical Logic: {exp.technicalReason}</span>
                              <span>Duration: {step.duration_ms}ms</span>
                            </div>
                          </div>
                        );
                      })()}

                      {/* Arguments Section */}
                      <div>
                        <div className="text-[10px] font-mono uppercase text-slate-500 mb-1 flex items-center gap-1">
                          <Terminal className="w-3 h-3 text-slate-400" /> Sanitized Arguments (Credentials Masked)
                        </div>
                        <pre className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 font-mono text-[11px] text-cyan-300 overflow-x-auto">
                          {JSON.stringify(step.sanitized_arguments || step.raw_arguments || {}, null, 2)}
                        </pre>
                      </div>

                      {/* Result / Output Section */}
                      <div>
                        <div className="text-[10px] font-mono uppercase text-slate-500 mb-1 flex items-center gap-1">
                          <FileCode className="w-3 h-3 text-slate-400" /> Tool Outcome Payload
                        </div>
                        <pre className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 font-mono text-[11px] text-slate-300 overflow-x-auto">
                          {JSON.stringify(step.tool_result || { note: 'Action was blocked by safety supervisor before tool execution.' }, null, 2)}
                        </pre>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
