import React, { useRef, useState } from 'react';
import {
  Play,
  Sliders,
  ShieldCheck,
  Bot,
  AlertCircle,
  Clock,
  Repeat,
  Layers,
  Sparkles,
  UploadCloud,
  Database,
  FileSpreadsheet,
  CheckCircle2,
  Table,
  BookOpen,
  ArrowRight,
  FileText,
  KeyRound,
  Hash,
  X,
  Download,
  Building,
  HeartPulse,
  GraduationCap,
  ShoppingCart,
} from 'lucide-react';
import { api } from '../services/api';
import { CreateWorkflowPayload, DatabaseUploadResponse, TableInfo } from '../types';

interface CreateWorkflowPageProps {
  onWorkflowCreated: (id: string) => void;
}

export const CreateWorkflowPage: React.FC<CreateWorkflowPageProps> = ({
  onWorkflowCreated,
}) => {
  const [task, setTask] = useState<string>('Inspect personnel records and compile readiness report for engineering department');
  const [agentType, setAgentType] = useState<string>('mock:normal_success');
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [maxSteps, setMaxSteps] = useState<number>(10);
  const [maxRepeats, setMaxRepeats] = useState<number>(3);
  const [maxDuration, setMaxDuration] = useState<number>(60);
  const [loopThreshold, setLoopThreshold] = useState<number>(2);
  const [submitting, setSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Database Upload & AI Teacher State
  const [uploadedDb, setUploadedDb] = useState<DatabaseUploadResponse | null>(null);
  const [uploading, setUploading] = useState<boolean>(false);
  const [activeTableTab, setActiveTableTab] = useState<string>('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const agentOptions = [
    {
      id: 'mock:db_explainer',
      name: 'Deterministic Agent: Database Explainer & Teacher',
      badge: 'AI Explainer',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      description: 'Inspects custom uploaded database (.db, .csv, .json), analyzes schema & relationships, and explains data in English & Tamil.',
    },
    {
      id: 'mock:normal_success',
      name: 'Deterministic Agent: Normal Progress',
      badge: 'Success Flow',
      badgeColor: 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20',
      description: 'Progresses logically through employee search, detail inspection, and report generation, then concludes.',
    },
    {
      id: 'mock:infinite_loop',
      name: 'Deterministic Agent: Cyclic Loop (A &rarr; B &rarr; A &rarr; B)',
      badge: 'Loop Test',
      badgeColor: 'text-rose-400 bg-rose-500/10 border-rose-500/20',
      description: 'Intentionally generates alternating tool calls to trigger and verify the Infinite-Loop Prevention Gate.',
    },
    {
      id: 'mock:repeated_calls',
      name: 'Deterministic Agent: Repeated Identical Calls',
      badge: 'Repeat Test',
      badgeColor: 'text-amber-400 bg-amber-500/10 border-amber-500/20',
      description: 'Calls the same tool repeatedly with identical or equivalent arguments to trigger the Repeated Tool-Call Gate.',
    },
    {
      id: 'mock:sensitive_action',
      name: 'Deterministic Agent: Sensitive HR / Salary Modification',
      badge: 'Approval Test',
      badgeColor: 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20',
      description: 'Attempts salary adjustments requiring human authorization. Pauses workflow until approved in Approval Center.',
    },
    {
      id: 'mock:no_progress',
      name: 'Deterministic Agent: Stagnant Outcome (No Progress)',
      badge: 'Progress Test',
      badgeColor: 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20',
      description: 'Repeatedly invokes static endpoints returning identical payloads with zero informational delta.',
    },
    {
      id: 'mock:timeout_failure',
      name: 'Deterministic Agent: Flaky Tool / Network Failure',
      badge: 'Resilience Test',
      badgeColor: 'text-purple-400 bg-purple-500/10 border-purple-500/20',
      description: 'Generates unhandled timeouts and exceptions to test resilience and bounded retry budgets.',
    },
    {
      id: 'gemini',
      name: 'Google Gemini 1.5 Flash (LLM Provider)',
      badge: 'Real LLM',
      badgeColor: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
      description: 'Dispatches actual task prompts to Google Gemini via GEMINI_API_KEY if configured in environment.',
    },
  ];

  const handleFileUpload = async (file: File) => {
    try {
      setUploading(true);
      setErrorMsg(null);
      const res = await api.uploadDatabase(file);
      setUploadedDb(res);
      if (res.tables && res.tables.length > 0) {
        setActiveTableTab(res.tables[0].name);
      }
      setAgentType('mock:db_explainer');
      setTask(
        `Explain the uploaded database '${res.filename}': Inspect table schemas, relationships, and analyze sample distributions in both English and Tamil.`
      );
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to parse database file.');
    } finally {
      setUploading(false);
    }
  };

  const handleLoadSampleDb = async (preset: string = 'university') => {
    try {
      setUploading(true);
      setErrorMsg(null);
      const res = await api.getSampleDatabase(preset);
      setUploadedDb(res);
      if (res.tables && res.tables.length > 0) {
        setActiveTableTab(res.tables[0].name);
      }
      setAgentType('mock:db_explainer');

      if (preset === 'banking') {
        setTask(
          `Teach and explain the Enterprise Banking Database ('bank_accounts', 'transactions', 'security_alerts'): Analyze risk distributions, transaction loops, and explain financial compliance in English & Tamil.`
        );
      } else if (preset === 'healthcare') {
        setTask(
          `Teach and explain the Healthcare Patient Registry: Analyze diagnoses, attending physicians, admission statistics, and patient billing in English & Tamil.`
        );
      } else if (preset === 'ecommerce') {
        setTask(
          `Teach and explain the E-Commerce Sales Dataset: Analyze product categories, order volumes, total revenues, and delivery statuses in English & Tamil.`
        );
      } else {
        setTask(
          `Teach and explain the University Database ('students', 'courses', 'grades'): Analyze entity relationships, student GPA metrics, and generate a structured student-friendly explanation in English & Tamil.`
        );
      }
    } catch (err: any) {
      setErrorMsg(`Failed to load ${preset} sample database.`);
    } finally {
      setUploading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!task.trim()) {
      setErrorMsg('Task instruction is required.');
      return;
    }

    try {
      setSubmitting(true);
      setErrorMsg(null);
      const payload: CreateWorkflowPayload = {
        task: task.trim(),
        agent_type: agentType,
        max_steps: maxSteps,
        max_repeated_calls: maxRepeats,
        max_duration_seconds: maxDuration,
        loop_cycle_threshold: loopThreshold,
      };

      const wf = await api.createWorkflow(payload, true);
      onWorkflowCreated(wf.id);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || err.message || 'Failed to initialize workflow.');
    } finally {
      setSubmitting(false);
    }
  };

  const activeTable = uploadedDb?.tables.find((t) => t.name === activeTableTab) || uploadedDb?.tables[0];

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fadeIn select-none">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
          <Bot className="w-6 h-6 text-indigo-400" />
          Initialize Agent Workflow
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Configure agent task, execution limits, or upload your own database (.db, .csv, .json) for AI-guided schema teaching and guarded analysis.
        </p>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* ========================================================================= */}
      {/* 📁 DATABASE UPLOAD & AI TEACHER SHOWCASE CARD                              */}
      {/* ========================================================================= */}
      <div className="glass-panel p-6 rounded-2xl border border-indigo-500/30 bg-slate-950/70 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 border border-cyan-500/30 flex items-center justify-center">
              <Database className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-white flex items-center gap-2">
                Upload Custom Database & AI Teacher Explainer
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  New Feature
                </span>
              </h2>
              <p className="text-[11px] text-slate-400">
                Upload SQLite (.db), CSV (.csv), or JSON (.json) &mdash; AI agent will inspect, query, and teach you the data safely
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handleLoadSampleDb('university')}
              disabled={uploading}
              className="px-3 py-1.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 text-xs font-mono transition flex items-center gap-1.5 shadow-sm"
            >
              <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
              <span>⚡ Load Sample University DB</span>
            </button>
          </div>
        </div>

        {/* Upload Drop Zone / Button */}
        {!uploadedDb ? (
          <div className="space-y-4">
            <div
              onClick={() => fileInputRef.current?.click()}
              className="p-8 border-2 border-dashed border-slate-700 hover:border-cyan-500/60 rounded-2xl bg-slate-900/40 hover:bg-slate-900/80 transition-all cursor-pointer text-center space-y-3 group"
            >
              <input
                type="file"
                ref={fileInputRef}
                onChange={(e) => {
                  if (e.target.files && e.target.files[0]) {
                    handleFileUpload(e.target.files[0]);
                  }
                }}
                accept=".db,.sqlite,.sqlite3,.csv,.json,.sql"
                className="hidden"
              />
              <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 mx-auto flex items-center justify-center group-hover:scale-110 transition">
                {uploading ? (
                  <div className="w-5 h-5 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                ) : (
                  <UploadCloud className="w-6 h-6 text-cyan-400" />
                )}
              </div>
              <div>
                <p className="text-sm font-bold text-white">
                  {uploading ? 'Parsing Database Schema & Tables...' : 'Click to Upload Your Database or Dataset'}
                </p>
                <p className="text-xs text-slate-400 mt-0.5 font-mono">
                  Drag & drop your .db, .sqlite, .csv, or .json file here, or choose a ready sample below:
                </p>
              </div>
            </div>

            {/* Ready-to-Use Sample Datasets Showcase */}
            <div className="space-y-2 pt-1">
              <div className="flex items-center justify-between">
                <span className="text-xs font-mono font-bold text-slate-300 uppercase tracking-wider flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-400" /> Ready-to-Use Sample Datasets (Download or 1-Click Load)
                </span>
                <span className="text-[10px] font-mono text-slate-500">Pick any to test immediately</span>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {[
                  {
                    id: 'students',
                    preset: 'students',
                    title: 'Student Academic Records',
                    filename: 'student_academic_records.csv',
                    type: 'CSV File',
                    records: '8 records',
                    icon: GraduationCap,
                    accentColor: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
                    desc: 'Student names, AI/CS departments, semester GPAs, attendance %, and placement status.',
                  },
                  {
                    id: 'banking',
                    preset: 'banking',
                    title: 'Enterprise Banking Vault',
                    filename: 'enterprise_banking_vault.db',
                    type: 'SQLite DB',
                    records: '3 tables • 11 records',
                    icon: Building,
                    accentColor: 'text-indigo-400 border-indigo-500/30 bg-indigo-500/10',
                    desc: 'Accounts, transactions, and security alerts with foreign keys for testing Gate 2 Approvals.',
                  },
                  {
                    id: 'healthcare',
                    preset: 'healthcare',
                    title: 'Healthcare Patient Registry',
                    filename: 'healthcare_patient_registry.csv',
                    type: 'CSV File',
                    records: '6 records',
                    icon: HeartPulse,
                    accentColor: 'text-rose-400 border-rose-500/30 bg-rose-500/10',
                    desc: 'Patient diagnoses, attending physicians, admission dates, and hospital billing.',
                  },
                  {
                    id: 'ecommerce',
                    preset: 'ecommerce',
                    title: 'E-Commerce Transactions',
                    filename: 'ecommerce_sales_transactions.csv',
                    type: 'CSV File',
                    records: '5 records',
                    icon: ShoppingCart,
                    accentColor: 'text-cyan-400 border-cyan-500/30 bg-cyan-500/10',
                    desc: 'Hardware orders, units, prices, totals, and delivery status tracking.',
                  },
                ].map((ds) => {
                  const Icon = ds.icon;
                  return (
                    <div
                      key={ds.id}
                      className="p-3.5 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition flex flex-col justify-between space-y-2.5"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <div className={`p-1.5 rounded-lg border ${ds.accentColor}`}>
                            <Icon className="w-4 h-4" />
                          </div>
                          <div>
                            <span className="font-bold text-xs text-white block leading-tight">{ds.title}</span>
                            <span className="text-[10px] font-mono text-slate-400">
                              {ds.filename} &bull; {ds.records}
                            </span>
                          </div>
                        </div>
                        <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                          {ds.type}
                        </span>
                      </div>

                      <p className="text-[11px] text-slate-400 leading-relaxed">{ds.desc}</p>

                      <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between gap-2">
                        <a
                          href={`/samples/${ds.filename}`}
                          download={ds.filename}
                          className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[10px] font-mono transition flex items-center gap-1 shadow-sm"
                          title={`Download ${ds.filename} to your computer`}
                        >
                          <Download className="w-3 h-3 text-cyan-400" />
                          <span>Download</span>
                        </a>

                        <button
                          type="button"
                          onClick={() => handleLoadSampleDb(ds.preset)}
                          disabled={uploading}
                          className="px-3 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-[11px] font-mono font-bold transition flex items-center gap-1 shadow-sm"
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>⚡ 1-Click Load</span>
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        ) : (
          /* Active Loaded Database Inspector */
          <div className="space-y-4 animate-fadeIn">
            <div className="p-4 rounded-xl bg-slate-900/90 border border-cyan-500/30 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-emerald-500/20 border border-emerald-500/30 flex items-center justify-center">
                  <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                </div>
                <div>
                  <div className="font-bold text-white text-sm flex items-center gap-2">
                    <span>{uploadedDb.filename}</span>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300">
                      {(uploadedDb.file_size_bytes / 1024).toFixed(1)} KB
                    </span>
                  </div>
                  <p className="text-[11px] text-cyan-300 font-mono mt-0.5">
                    {uploadedDb.table_count} Table(s) &bull; {uploadedDb.total_records} Total Records &bull; {uploadedDb.database_type}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-[11px] font-mono transition"
                >
                  Change File
                </button>
                <button
                  type="button"
                  onClick={() => setUploadedDb(null)}
                  className="p-1 rounded-lg text-slate-500 hover:text-rose-400 transition"
                  title="Remove"
                >
                  <X className="w-4 h-4" />
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={(e) => {
                    if (e.target.files && e.target.files[0]) {
                      handleFileUpload(e.target.files[0]);
                    }
                  }}
                  accept=".db,.sqlite,.sqlite3,.csv,.json,.sql"
                  className="hidden"
                />
              </div>
            </div>

            {/* Table Tabs */}
            {uploadedDb.tables.length > 0 && (
              <div className="space-y-3">
                <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                  <span className="text-[11px] font-mono text-slate-400 mr-1 flex items-center gap-1">
                    <Table className="w-3.5 h-3.5" /> Tables:
                  </span>
                  {uploadedDb.tables.map((t) => (
                    <button
                      key={t.name}
                      type="button"
                      onClick={() => setActiveTableTab(t.name)}
                      className={`px-3 py-1 rounded-lg text-xs font-mono transition flex items-center gap-1.5 ${
                        activeTable?.name === t.name
                          ? 'bg-indigo-600 text-white font-bold shadow-sm'
                          : 'bg-slate-900 text-slate-400 hover:text-white'
                      }`}
                    >
                      <span>{t.name}</span>
                      <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-950/60 text-slate-300">
                        {t.row_count}
                      </span>
                    </button>
                  ))}
                </div>

                {/* Selected Table Schema & Sample Preview */}
                {activeTable && (
                  <div className="p-3.5 rounded-xl bg-[#080C14] border border-slate-800 space-y-3">
                    <div className="flex items-center justify-between text-xs">
                      <div className="font-mono font-bold text-slate-200 flex items-center gap-2">
                        <span>Schema for '{activeTable.name}':</span>
                        <span className="text-[11px] text-slate-400 font-normal">
                          {activeTable.columns.length} columns &bull; {activeTable.row_count} rows
                        </span>
                      </div>
                    </div>

                    {/* Columns Badges */}
                    <div className="flex flex-wrap gap-1.5">
                      {activeTable.columns.map((col) => (
                        <span
                          key={col.name}
                          className={`text-[10px] font-mono px-2 py-0.5 rounded-md border flex items-center gap-1 ${
                            col.is_primary_key
                              ? 'bg-amber-500/10 text-amber-300 border-amber-500/30'
                              : 'bg-slate-900 text-slate-300 border-slate-800'
                          }`}
                        >
                          {col.is_primary_key && <KeyRound className="w-2.5 h-2.5 text-amber-400" />}
                          <span className="font-semibold">{col.name}</span>
                          <span className="text-slate-500 text-[9px] uppercase">{col.type}</span>
                        </span>
                      ))}
                    </div>

                    {/* Preview Rows Table */}
                    {activeTable.preview_rows.length > 0 && (
                      <div className="overflow-x-auto rounded-lg border border-slate-800/80">
                        <table className="w-full text-left text-[11px] font-mono">
                          <thead className="bg-slate-900 text-slate-400 uppercase text-[9px]">
                            <tr>
                              {activeTable.columns.map((c) => (
                                <th key={c.name} className="py-1.5 px-2.5">
                                  {c.name}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-slate-800/60 bg-slate-950/40">
                            {activeTable.preview_rows.map((row, idx) => (
                              <tr key={idx} className="hover:bg-slate-900/50">
                                {activeTable.columns.map((c) => (
                                  <td key={c.name} className="py-1.5 px-2.5 text-slate-300 truncate max-w-[150px]">
                                    {String(row[c.name] ?? '')}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Quick 1-Click Teaching & Explaining Prompts */}
            <div className="pt-2 border-t border-slate-800/80 space-y-2">
              <span className="text-[11px] font-mono text-slate-400 block">
                💡 1-Click Teaching & Analysis Actions:
              </span>
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 text-xs">
                <button
                  type="button"
                  onClick={() => {
                    setAgentType('mock:db_explainer');
                    setTask(
                      `Teach and explain the database '${uploadedDb.filename}': Describe entity relationships, foreign keys, table purposes, and summary in English and Tamil.`
                    );
                  }}
                  className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-cyan-500/50 text-left transition flex flex-col justify-between"
                >
                  <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                    <BookOpen className="w-3.5 h-3.5 text-cyan-400" /> 1. Teach & Explain DB
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">Full ERD & Schema explanation in English + Tamil</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setAgentType('mock:db_explainer');
                    setTask(
                      `Analyze data in '${uploadedDb.filename}': Execute safe aggregate queries, group student GPA distributions, and summarize key insights.`
                    );
                  }}
                  className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-indigo-500/50 text-left transition flex flex-col justify-between"
                >
                  <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                    <Hash className="w-3.5 h-3.5 text-indigo-400" /> 2. Query Analytics
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">Execute safe aggregations, metrics & top performers</span>
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setAgentType('mock:db_explainer');
                    setTask(
                      `Safety Test on '${uploadedDb.filename}': Attempt to DROP TABLE or delete records to verify LoopGuard Gate 2 Human Approval Interception.`
                    );
                  }}
                  className="p-2.5 rounded-xl bg-slate-900 hover:bg-slate-800 border border-slate-800 hover:border-rose-500/50 text-left transition flex flex-col justify-between"
                >
                  <span className="font-bold text-white flex items-center gap-1.5 text-xs">
                    <ShieldCheck className="w-3.5 h-3.5 text-rose-400" /> 3. Test Safety Gate
                  </span>
                  <span className="text-[10px] text-slate-400 mt-1">Simulate DROP TABLE & verify Approval Center interception</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Workflow Form */}
      <form onSubmit={handleSubmit} className="glass-panel p-6 sm:p-8 rounded-2xl border border-slate-800 space-y-6">
        {/* Task Input */}
        <div className="space-y-2">
          <label htmlFor="workflow-task-input" className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
            Task Instruction / Goal <span className="text-rose-400">*</span>
          </label>
          <textarea
            id="workflow-task-input"
            rows={3}
            value={task}
            onChange={(e) => setTask(e.target.value)}
            placeholder="Describe what the agent should accomplish..."
            className="w-full px-4 py-3 rounded-xl bg-slate-900/80 border border-slate-700/80 text-white placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition"
          />
        </div>

        {/* Agent Persona / Scenario Selection */}
        <div className="space-y-3">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-300">
            Select Agent Execution Profile
          </label>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {agentOptions.map((opt) => {
              const isSelected = agentType === opt.id;
              return (
                <div
                  key={opt.id}
                  id={`agent-option-${opt.id}`}
                  onClick={() => setAgentType(opt.id)}
                  className={`p-4 rounded-xl border text-left cursor-pointer transition-all ${
                    isSelected
                      ? 'border-indigo-500 bg-indigo-950/20 shadow-glow-cyan'
                      : 'border-slate-800 bg-slate-900/40 hover:bg-slate-800/60'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <span className={`w-2 h-2 rounded-full ${isSelected ? 'bg-indigo-400' : 'bg-slate-600'}`}></span>
                      {opt.name}
                    </span>
                    <span className={`text-[10px] font-semibold px-2 py-0.5 rounded border ${opt.badgeColor}`}>
                      {opt.badge}
                    </span>
                  </div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {opt.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Execution Limits Toggle */}
        <div className="pt-2 border-t border-slate-800/80">
          <button
            type="button"
            id="toggle-advanced-limits-btn"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-2 text-xs font-semibold text-indigo-400 hover:text-indigo-300 transition"
          >
            <Sliders className="w-3.5 h-3.5" />
            {showAdvanced ? 'Hide Custom Execution Limits' : 'Configure Custom Execution Limits & Thresholds'}
          </button>

          {showAdvanced && (
            <div className="mt-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-fadeIn">
              <div>
                <label htmlFor="max-steps-input" className="block text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1">
                  <Layers className="w-3 h-3 text-indigo-400" /> Max Steps
                </label>
                <input
                  id="max-steps-input"
                  type="number"
                  min={1}
                  max={50}
                  value={maxSteps}
                  onChange={(e) => setMaxSteps(parseInt(e.target.value) || 10)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs font-mono"
                />
              </div>

              <div>
                <label htmlFor="max-repeats-input" className="block text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1">
                  <Repeat className="w-3 h-3 text-amber-400" /> Max Repeats
                </label>
                <input
                  id="max-repeats-input"
                  type="number"
                  min={1}
                  max={10}
                  value={maxRepeats}
                  onChange={(e) => setMaxRepeats(parseInt(e.target.value) || 3)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs font-mono"
                />
              </div>

              <div>
                <label htmlFor="max-duration-input" className="block text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-cyan-400" /> Timeout (s)
                </label>
                <input
                  id="max-duration-input"
                  type="number"
                  min={5}
                  max={600}
                  value={maxDuration}
                  onChange={(e) => setMaxDuration(parseFloat(e.target.value) || 60)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs font-mono"
                />
              </div>

              <div>
                <label htmlFor="loop-threshold-input" className="block text-[11px] font-mono text-slate-400 mb-1 flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-rose-400" /> Cycle Threshold
                </label>
                <input
                  id="loop-threshold-input"
                  type="number"
                  min={2}
                  max={5}
                  value={loopThreshold}
                  onChange={(e) => setLoopThreshold(parseInt(e.target.value) || 2)}
                  className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-white text-xs font-mono"
                />
              </div>
            </div>
          )}
        </div>

        {/* Submit */}
        <div className="pt-4 flex items-center justify-end gap-3">
          <button
            type="submit"
            id="start-workflow-submit-btn"
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm shadow-lg shadow-indigo-600/30 transition disabled:opacity-50"
          >
            {submitting ? (
              <>
                <div className="w-4 h-4 border-2 border-white/20 border-t-white rounded-full animate-spin" />
                Initializing...
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-white" />
                Start Workflow
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};
