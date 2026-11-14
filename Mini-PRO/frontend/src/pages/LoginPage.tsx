import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  GraduationCap,
  Code2,
  ShieldCheck,
  Lock,
  User,
  ArrowRight,
  ArrowLeft,
  CheckCircle2,
  Terminal,
  Activity,
  Database,
  UserPlus,
  LogIn,
  AlertCircle,
  Building,
  Server,
  Cpu,
  Clock,
  RefreshCw,
  Hash,
  BarChart2,
  ChevronDown,
  ChevronUp,
  Maximize2,
  X,
  Sparkles,
  Shield,
} from 'lucide-react';
import { UserProfile } from '../types';
import { api } from '../services/api';
import { useTheme } from '../context/ThemeContext';
import { ThemeToggle } from '../components/ThemeToggle';

interface LoginPageProps {
  onLogin: (profile: UserProfile) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onLogin }) => {
  const { theme } = useTheme();
  const isLight = theme === 'light';
  // Navigation view: 'landing' (architecture showcase) | 'signin' | 'signup'
  const [viewMode, setViewMode] = useState<'landing' | 'signin' | 'signup'>('landing');
  const [authMode, setAuthMode] = useState<'signin' | 'signup'>('signin');

  const [selectedRole, setSelectedRole] = useState<'student' | 'developer' | 'security_lead'>('student');
  const [name, setName] = useState<string>('Dhinesha Gnanavel');
  const [email, setEmail] = useState<string>('dhinesha@loopguard.ai');
  const [organization, setOrganization] = useState<string>('Department of AI & Data Science');
  const [password, setPassword] = useState<string>('password123');
  const [isAuthenticating, setIsAuthenticating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Architecture Banner Showcase State
  const [showArchitecture, setShowArchitecture] = useState<boolean>(true);
  const [isImageZoomed, setIsImageZoomed] = useState<boolean>(false);
  const [activeGateInfo, setActiveGateInfo] = useState<string | null>(null);

  // Backend Health State
  const [backendStatus, setBackendStatus] = useState<{
    connected: boolean;
    dbConnected: boolean;
    dbType: string;
    message: string;
  }>({
    connected: true,
    dbConnected: true,
    dbType: 'SQLite Native DB',
    message: 'Backend Safety Engine & Persistent Database Online',
  });

  useEffect(() => {
    // Check backend database health
    api
      .getHealth()
      .then((health: any) => {
        setBackendStatus({
          connected: health.status === 'healthy',
          dbConnected: health.database_connected,
          dbType: health.database_type || (health.supabase_configured ? 'Supabase Cloud DB' : 'SQLite Native DB'),
          message: health.database_connected
            ? 'Backend Safety Engine & Database Active'
            : 'Backend Engine Connected (Initializing Storage)',
        });
      })
      .catch(() => {
        setBackendStatus({
          connected: false,
          dbConnected: false,
          dbType: 'SQLite Native DB',
          message: 'Connecting to Backend Safety Engine...',
        });
      });
  }, []);

  const personas = [
    {
      id: 'student' as const,
      title: 'Student / AI Researcher',
      icon: GraduationCap,
      badge: 'Academic / Viva Mode',
      badgeColor: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
      description: 'Interactive execution flowcharts, visual loop explainers, and instant PDF/JSON project audit report export.',
      defaultName: 'Dhinesha Gnanavel (Student)',
      defaultEmail: 'dhinesha@loopguard.ai',
      defaultOrg: 'Department of Computer Science & AI',
      avatarColor: 'from-emerald-500 to-cyan-500',
    },
    {
      id: 'developer' as const,
      title: 'Software Developer / AI Engineer',
      icon: Code2,
      badge: 'Engineering Mode',
      badgeColor: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      description: 'Raw SHA-256 hash inspection, Model Context Protocol (MCP) tool dispatching, execution durations, and retry metrics.',
      defaultName: 'Alex Mercer (Lead Agent Engineer)',
      defaultEmail: 'alex.mercer@devcorp.io',
      defaultOrg: 'Autonomous Agent Engineering Core',
      avatarColor: 'from-cyan-500 to-indigo-500',
    },
    {
      id: 'security_lead' as const,
      title: 'Security Lead / Enterprise Admin',
      icon: ShieldCheck,
      badge: 'SOC 2 Governance Mode',
      badgeColor: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
      description: 'Human-in-the-Loop approval gate sign-off, runtime safety threshold controls, and strict compliance audit logging.',
      defaultName: 'Sarah Jenkins (Security Architect)',
      defaultEmail: 'sarah.jenkins@enterprise-sec.com',
      defaultOrg: 'Global AI Governance & Compliance Office',
      avatarColor: 'from-purple-500 to-rose-500',
    },
  ];

  const gatesList = [
    {
      id: 'step_time',
      title: 'Step & Time Limit',
      icon: Clock,
      desc: 'Prevents runaway execution through bounded step thresholds and max execution timeouts.',
      color: 'border-cyan-500/40 text-cyan-300 bg-cyan-500/10',
    },
    {
      id: 'sensitive_tool',
      title: 'Sensitive Tool Check',
      icon: ShieldAlert,
      desc: 'Intercepts high-risk mutations (salary adjustments, database wipes) for Human Authorization.',
      color: 'border-amber-500/40 text-amber-300 bg-amber-500/10',
    },
    {
      id: 'repeated_call',
      title: 'Repeated Call Check',
      icon: Hash,
      desc: 'Normalizes JSON argument semantics with SHA-256 to stop duplicate redundant calls.',
      color: 'border-indigo-500/40 text-indigo-300 bg-indigo-500/10',
    },
    {
      id: 'loop_cycle',
      title: 'Loop Cycle Detection',
      icon: RefreshCw,
      desc: 'Sliding-window N-Gram algorithm discovers alternating oscillatory cycles (A -> B -> A -> B).',
      color: 'border-purple-500/40 text-purple-300 bg-purple-500/10',
    },
    {
      id: 'no_progress',
      title: 'No-Progress Check',
      icon: BarChart2,
      desc: 'Evaluates output entropy deltas to terminate stagnant agents repeating static responses.',
      color: 'border-rose-500/40 text-rose-300 bg-rose-500/10',
    },
  ];

  const handlePersonaSelect = (roleId: 'student' | 'developer' | 'security_lead') => {
    setSelectedRole(roleId);
    const p = personas.find((item) => item.id === roleId);
    if (p) {
      setName(p.defaultName);
      setEmail(p.defaultEmail);
      setOrganization(p.defaultOrg);
    }
  };

  const handleNavigateToAuth = (mode: 'signin' | 'signup') => {
    setAuthMode(mode);
    setViewMode(mode);
    setErrorMessage(null);
    setSuccessMessage(null);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setSuccessMessage(null);
    setIsAuthenticating(true);

    try {
      if (authMode === 'signup') {
        // Call Backend Native Auth Signup Endpoint (POST /api/v1/auth/signup)
        const userRes = await api.signUp({
          name: name.trim() || 'Authorized User',
          email: email.trim().toLowerCase(),
          password: password,
          role: selectedRole,
          organization: organization.trim() || 'Department of AI',
        });

        const avatarColor =
          selectedRole === 'student'
            ? 'from-emerald-500 to-cyan-500'
            : selectedRole === 'developer'
            ? 'from-cyan-500 to-indigo-500'
            : 'from-purple-500 to-rose-500';

        const userProfile: UserProfile = {
          name: userRes.name,
          email: userRes.email,
          role: (userRes.role as any) || selectedRole,
          organization: userRes.organization || organization,
          avatarColor,
          studentModeEnabled: selectedRole === 'student',
          loginTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        localStorage.setItem('loopguard_user', JSON.stringify(userProfile));
        setSuccessMessage('Account created and saved to Backend Database! Entering Control Center...');
        setTimeout(() => onLogin(userProfile), 500);
      } else {
        // Call Backend Native Auth Login Endpoint (POST /api/v1/auth/login)
        const userRes = await api.login({
          email: email.trim().toLowerCase(),
          password: password,
          role: selectedRole,
        });

        const avatarColor =
          selectedRole === 'student'
            ? 'from-emerald-500 to-cyan-500'
            : selectedRole === 'developer'
            ? 'from-cyan-500 to-indigo-500'
            : 'from-purple-500 to-rose-500';

        const userProfile: UserProfile = {
          name: userRes.name,
          email: userRes.email,
          role: (userRes.role as any) || selectedRole,
          organization: userRes.organization || organization,
          avatarColor,
          studentModeEnabled: selectedRole === 'student',
          loginTime: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        };

        localStorage.setItem('loopguard_user', JSON.stringify(userProfile));
        setSuccessMessage('Successfully authenticated with Backend Database! Entering Control Center...');
        setTimeout(() => onLogin(userProfile), 500);
      }
    } catch (err: any) {
      console.error('Auth error:', err);
      const detail =
        err.response?.data?.detail ||
        err.message ||
        'Authentication failed. Please verify credentials or create an account.';
      setErrorMessage(detail);
      setIsAuthenticating(false);
    }
  };

  return (
    <div
      className={`min-h-screen flex flex-col relative overflow-hidden select-none transition-colors duration-200 ${
        isLight ? 'bg-[#F8FAFC] text-slate-800' : 'bg-[#070A12] text-slate-100'
      }`}
    >
      {/* Ambient Glow Backdrop */}
      <div
        className={`absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[850px] h-[550px] rounded-full blur-[150px] pointer-events-none transition-colors ${
          isLight ? 'bg-indigo-200/40' : 'bg-indigo-600/15'
        }`}
      />
      <div
        className={`absolute bottom-10 right-10 w-96 h-96 rounded-full blur-[130px] pointer-events-none transition-colors ${
          isLight ? 'bg-cyan-200/30' : 'bg-cyan-600/10'
        }`}
      />
      <div
        className={`absolute top-10 left-10 w-96 h-96 rounded-full blur-[130px] pointer-events-none transition-colors ${
          isLight ? 'bg-purple-200/30' : 'bg-purple-600/10'
        }`}
      />

      {/* Security Engine Grid Lines */}
      <div
        className={`absolute inset-0 pointer-events-none ${isLight ? 'opacity-[0.05]' : 'opacity-[0.03]'}`}
        style={{
          backgroundImage: isLight
            ? 'linear-gradient(to right, #0f172a 1px, transparent 1px), linear-gradient(to bottom, #0f172a 1px, transparent 1px)'
            : 'linear-gradient(to right, #ffffff 1px, transparent 1px), linear-gradient(to bottom, #ffffff 1px, transparent 1px)',
          backgroundSize: '40px 40px',
        }}
      />

      {/* Fullscreen Image Zoom Modal */}
      {isImageZoomed && (
        <div
          className="fixed inset-0 z-50 bg-black/90 backdrop-blur-lg flex flex-col items-center justify-center p-4 animate-fadeIn"
          onClick={() => setIsImageZoomed(false)}
        >
          <div className="relative max-w-5xl w-full bg-slate-950 p-3 rounded-3xl border border-cyan-500/40 shadow-2xl">
            <button
              onClick={() => setIsImageZoomed(false)}
              className="absolute -top-3 -right-3 p-2 rounded-full bg-slate-800 text-white hover:bg-slate-700 border border-slate-700 shadow-xl"
            >
              <X className="w-5 h-5" />
            </button>
            <img
              src="/loopguard-architecture.jpg"
              alt="LoopGuard Backend Loop Engine Full Architecture"
              className="w-full h-auto rounded-2xl shadow-2xl"
            />
            <div className="mt-3 text-center text-xs font-mono text-cyan-300">
              LoopGuard Backend Loop Engine &bull; Safe AI Agents &bull; Controlled Execution &bull; Click anywhere to close
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* TOP HEADER NAVIGATION BAR WITH THEME TOGGLE, LOGIN & CREATE ACCOUNT       */}
      {/* ========================================================================= */}
      <header
        className={`w-full sticky top-0 z-40 transition-colors duration-200 border-b backdrop-blur-md ${
          isLight
            ? 'bg-white/90 border-slate-200 shadow-sm'
            : 'bg-[#070A12]/90 border-slate-800/80 shadow-lg'
        }`}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          {/* Left Brand Trigger - Never Shrinks, Perfectly Aligned */}
          <div
            onClick={() => setViewMode('landing')}
            className="flex items-center gap-2.5 sm:gap-3 cursor-pointer group flex-shrink-0 select-none"
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-[1px] shadow-glow-cyan flex-shrink-0">
              <div
                className={`w-full h-full rounded-xl flex items-center justify-center ${
                  isLight ? 'bg-white' : 'bg-[#0B0F19]'
                }`}
              >
                <ShieldAlert className="w-4 h-4 text-indigo-600 dark:text-cyan-400 group-hover:scale-110 transition" />
              </div>
            </div>
            <div className="flex items-center gap-1.5 sm:gap-2 leading-none">
              <span className={`font-extrabold text-base tracking-tight font-mono whitespace-nowrap ${isLight ? 'text-slate-900' : 'text-white'}`}>
                Loop<span className="text-cyan-500">Guard</span>
              </span>
              <span className="inline-flex items-center text-[10px] font-mono px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-600 dark:text-indigo-300 border border-indigo-500/30 font-semibold uppercase whitespace-nowrap leading-none">
                Backend Loop Engine
              </span>
            </div>
          </div>

          {/* Center Database Live Status (Desktop) */}
          <div className={`hidden md:flex items-center gap-2 text-xs font-mono ${isLight ? 'text-slate-600' : 'text-slate-400'}`}>
            <div
              className={`w-2 h-2 rounded-full ${
                backendStatus.dbConnected ? 'bg-emerald-500 live-indicator' : 'bg-amber-400'
              }`}
            />
            <span className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-cyan-500" />
              <span>{backendStatus.dbType}:</span> <strong className="text-emerald-500 font-bold">ONLINE</strong>
            </span>
          </div>

          {/* RIGHT SIDE: THEME TOGGLE + LOGIN AND CREATE ACCOUNT */}
          <div className="flex items-center gap-2 sm:gap-2.5">
            {/* ☀️/🌙 Theme Switcher */}
            <ThemeToggle variant="compact" />

            {viewMode === 'landing' ? (
              <>
                <button
                  type="button"
                  id="header-login-btn"
                  onClick={() => handleNavigateToAuth('signin')}
                  className={`flex items-center gap-1.5 px-3.5 sm:px-4 py-2 rounded-xl text-xs font-mono font-bold transition shadow-sm ${
                    isLight
                      ? 'bg-white hover:bg-slate-100 border border-slate-300 text-slate-800 hover:text-indigo-600 hover:border-indigo-400'
                      : 'bg-slate-900/90 hover:bg-slate-800 border border-slate-700 hover:border-cyan-500/60 text-slate-200 hover:text-white'
                  }`}
                >
                  <LogIn className="w-3.5 h-3.5 text-cyan-500" />
                  <span>Log In</span>
                </button>

                <button
                  type="button"
                  id="header-signup-btn"
                  onClick={() => handleNavigateToAuth('signup')}
                  className="flex items-center gap-1.5 px-3.5 sm:px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-xs font-mono font-bold text-white shadow-md shadow-indigo-600/20 transition hover:shadow-cyan-500/30"
                >
                  <UserPlus className="w-3.5 h-3.5" />
                  <span>Create Account</span>
                </button>
              </>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setViewMode('landing')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-mono transition ${
                    isLight
                      ? 'bg-white hover:bg-slate-100 border-slate-300 text-slate-700'
                      : 'bg-slate-900 hover:bg-slate-800 border-slate-700 text-slate-300'
                  }`}
                >
                  <ArrowLeft className="w-3.5 h-3.5 text-cyan-500" />
                  <span>Architecture</span>
                </button>

                {viewMode === 'signin' ? (
                  <button
                    type="button"
                    onClick={() => handleNavigateToAuth('signup')}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 text-xs font-mono font-bold text-white shadow-md transition"
                  >
                    <UserPlus className="w-3.5 h-3.5" />
                    <span>Create Account</span>
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleNavigateToAuth('signin')}
                    className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-mono font-bold text-white shadow-md transition"
                  >
                    <LogIn className="w-3.5 h-3.5" />
                    <span>Log In</span>
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 flex flex-col items-center justify-center px-4 py-8 relative z-10">
        {/* ========================================================================= */}
        {/* VIEW 1: ARCHITECTURE SHOWCASE & HERO LANDING (DEFAULT VIEW)               */}
        {/* ========================================================================= */}
        {viewMode === 'landing' && (
          <div className="w-full max-w-5xl space-y-6 animate-fadeIn">
            {/* Hero Title Section */}
            <div className="text-center space-y-3 pt-2">
              <div className="inline-flex items-center gap-2 p-1.5 px-3.5 rounded-full bg-slate-900/90 border border-slate-800 shadow-2xl backdrop-blur-md">
                <ShieldAlert className="w-4 h-4 text-cyan-400" />
                <span className="font-mono text-xs text-slate-300">
                  Loop<span className="text-cyan-400">Guard</span> &bull; Safe AI Agents. Controlled Execution.
                </span>
              </div>

              <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Autonomous Agent{' '}
                <span className="bg-gradient-to-r from-cyan-400 via-indigo-300 to-purple-400 bg-clip-text text-transparent">
                  Safety & Loop Prevention
                </span>{' '}
                Control Center
              </h1>
              <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto">
                Safe AI Agents. Controlled Execution. Deterministic pre-execution safety supervisor, sliding-window cyclic loop detection, and backend persistent identity vault.
              </p>
            </div>

            {/* ARCHITECTURE SHOWCASE CARD (User Diagram: AI Robot -> 5 Gates -> Outcomes) */}
            <div className="glass-panel rounded-3xl border border-indigo-500/30 shadow-2xl backdrop-blur-xl bg-slate-950/70 overflow-hidden relative">
              <div className="p-4 sm:p-5 border-b border-slate-800/80 flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse" />
                  <span className="font-mono text-xs font-bold uppercase tracking-wider text-cyan-300 flex items-center gap-2">
                    <Sparkles className="w-3.5 h-3.5 text-cyan-400" /> LoopGuard Backend Loop Engine Architecture
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setIsImageZoomed(true)}
                    className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px] font-mono transition"
                    title="Expand Full Diagram"
                  >
                    <Maximize2 className="w-3 h-3 text-cyan-400" />
                    <span className="hidden sm:inline">Zoom Fullscreen</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setShowArchitecture(!showArchitecture)}
                    className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 text-[11px] font-mono transition"
                  >
                    <span>{showArchitecture ? 'Hide Diagram' : 'Show Diagram'}</span>
                    {showArchitecture ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {showArchitecture && (
                <div className="p-4 sm:p-6 space-y-4 animate-fadeIn">
                  {/* Graphic Banner */}
                  <div
                    className="relative rounded-2xl overflow-hidden border border-slate-800/90 shadow-2xl cursor-pointer group bg-[#060A14]"
                    onClick={() => setIsImageZoomed(true)}
                  >
                    <img
                      src="/loopguard-architecture.jpg"
                      alt="LoopGuard Backend Loop Engine - Safe AI Agents Controlled Execution"
                      className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-[1.01]"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-slate-950/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-between p-4 text-xs font-mono text-cyan-300">
                      <span>LoopGuard: Safe AI Agents &bull; Controlled Execution</span>
                      <span className="flex items-center gap-1 bg-slate-900/90 px-2.5 py-1 rounded-lg border border-cyan-500/40">
                        <Maximize2 className="w-3.5 h-3.5" /> Click to Enlarge
                      </span>
                    </div>
                  </div>

                  {/* 5 Safety Gates Overview */}
                  <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 pt-1">
                    {gatesList.map((gate) => {
                      const Icon = gate.icon;
                      const isSelected = activeGateInfo === gate.id;
                      return (
                        <button
                          key={gate.id}
                          type="button"
                          onClick={() => setActiveGateInfo(isSelected ? null : gate.id)}
                          className={`p-2.5 rounded-xl border text-left transition flex flex-col justify-between ${
                            isSelected
                              ? 'bg-slate-900 border-cyan-400 shadow-md shadow-cyan-500/20'
                              : 'bg-slate-900/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900/80'
                          }`}
                        >
                          <div className="flex items-center gap-1.5 mb-1">
                            <div className={`p-1 rounded-md border ${gate.color}`}>
                              <Icon className="w-3 h-3" />
                            </div>
                            <span className="text-[11px] font-bold text-white leading-tight">{gate.title}</span>
                          </div>
                          <span className="text-[10px] font-mono text-slate-400">Gate {gatesList.indexOf(gate) + 1} of 5</span>
                        </button>
                      );
                    })}
                  </div>

                  {/* Gate Explainer Tooltip Card */}
                  {activeGateInfo && (
                    <div className="p-3 rounded-xl bg-slate-900/90 border border-cyan-500/30 text-xs font-mono text-cyan-200 flex items-center justify-between animate-fadeIn">
                      <div className="flex items-center gap-2">
                        <Sparkles className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                        <span>{gatesList.find((g) => g.id === activeGateInfo)?.desc}</span>
                      </div>
                      <button
                        type="button"
                        onClick={() => setActiveGateInfo(null)}
                        className="text-slate-400 hover:text-white text-[10px] ml-2"
                      >
                        ✕ Close
                      </button>
                    </div>
                  )}

                  {/* 3 Core Gate Decisions Ribbon */}
                  <div className="flex flex-wrap items-center justify-between gap-2 pt-2 border-t border-slate-800/80 text-[11px] font-mono">
                    <div className="flex items-center gap-2">
                      <span className="text-slate-400">Decisions:</span>
                      <span className="px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3" /> ALLOW (Execute Tool)
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/30 font-bold flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> BLOCK (Stop Workflow)
                      </span>
                      <span className="px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 border border-amber-500/30 font-bold flex items-center gap-1">
                        <Clock className="w-3 h-3" /> APPROVAL (Wait for Human)
                      </span>
                    </div>
                    <span className="text-slate-400 font-semibold text-[10px]">
                      Loop Prevention &bull; Safe Execution &bull; Reliable AI
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Quick Action Cards Underneath Diagram */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div
                onClick={() => handleNavigateToAuth('signin')}
                className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-cyan-500/50 hover:bg-slate-900 transition-all cursor-pointer group flex items-center justify-between"
              >
                <div className="space-y-1">
                  <div className="font-bold text-sm text-white flex items-center gap-2">
                    <LogIn className="w-4 h-4 text-cyan-400" /> Existing Member / Evaluator
                  </div>
                  <p className="text-xs text-slate-400">
                    Sign in with Student, Developer, or Security Admin persona.
                  </p>
                </div>
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl bg-slate-800 group-hover:bg-cyan-600 text-white font-mono text-xs font-bold transition flex items-center gap-1.5 shadow"
                >
                  <span>Log In</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
                </button>
              </div>

              <div
                onClick={() => handleNavigateToAuth('signup')}
                className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900 transition-all cursor-pointer group flex items-center justify-between"
              >
                <div className="space-y-1">
                  <div className="font-bold text-sm text-white flex items-center gap-2">
                    <UserPlus className="w-4 h-4 text-indigo-400" /> New AI Researcher / Engineer
                  </div>
                  <p className="text-xs text-slate-400">
                    Create a new account stored directly in the backend SQLite DB.
                  </p>
                </div>
                <button
                  type="button"
                  className="px-4 py-2 rounded-xl bg-gradient-to-r from-indigo-600 to-cyan-500 text-white font-mono text-xs font-bold transition flex items-center gap-1.5 shadow"
                >
                  <span>Create Account</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
                </button>
              </div>
            </div>

            {/* Backend Database Live Status Banner */}
            <div className="flex flex-wrap items-center justify-between p-3 px-4 rounded-2xl bg-slate-900/80 border border-slate-800 text-xs backdrop-blur-md gap-2">
              <div className="flex items-center gap-2.5">
                <div
                  className={`w-2.5 h-2.5 rounded-full ${
                    backendStatus.dbConnected ? 'bg-emerald-400 live-indicator' : 'bg-amber-400'
                  }`}
                />
                <span className="text-slate-300 font-mono text-[11px] flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-400" />
                  Backend Database:&nbsp;
                  <strong className="text-emerald-400">
                    {backendStatus.dbConnected ? 'CONNECTED (safety_engine.db)' : 'CONNECTING'}
                  </strong>
                </span>
              </div>

              <div className="flex items-center gap-3 text-slate-400 font-mono text-[11px]">
                <span className="flex items-center gap-1">
                  <Server className="w-3.5 h-3.5 text-indigo-400" /> FastAPI Native Auth
                </span>
                <span className="text-slate-600">&bull;</span>
                <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                  <Cpu className="w-3.5 h-3.5 text-emerald-400" /> HMAC-SHA256 Encrypted
                </span>
              </div>
            </div>
          </div>
        )}

        {/* ========================================================================= */}
        {/* VIEW 2 & 3: DEDICATED LOGIN / SIGNUP AUTHENTICATION PAGE                  */}
        {/* ========================================================================= */}
        {(viewMode === 'signin' || viewMode === 'signup') && (
          <div className="w-full max-w-4xl space-y-6 animate-fadeIn">
            {/* Header with Back Navigation */}
            <div className="flex items-center justify-between">
              <button
                type="button"
                onClick={() => setViewMode('landing')}
                className="flex items-center gap-2 text-xs font-mono text-cyan-400 hover:text-cyan-300 transition"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Architecture Overview
              </button>
              <span className="text-[11px] font-mono text-slate-500">
                LoopGuard v1.0 &bull; Native Backend Security Engine
              </span>
            </div>

            {/* Auth Glass Card */}
            <div className="glass-panel p-6 sm:p-8 rounded-3xl border border-slate-800/80 shadow-2xl backdrop-blur-xl relative overflow-hidden bg-slate-950/80">
              <div className="absolute top-0 right-0 w-48 h-1 bg-gradient-to-r from-cyan-500 via-indigo-500 to-purple-500" />

              {/* Mode Switcher Tabs */}
              <div className="flex items-center p-1 rounded-2xl bg-slate-950/80 border border-slate-800/80 mb-6 max-w-sm">
                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('signin');
                    setViewMode('signin');
                    setErrorMessage(null);
                  }}
                  className={`flex-1 py-2 rounded-xl text-xs font-bold font-mono transition flex items-center justify-center gap-2 ${
                    authMode === 'signin'
                      ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <LogIn className="w-3.5 h-3.5" /> Log In
                </button>

                <button
                  type="button"
                  onClick={() => {
                    setAuthMode('signup');
                    setViewMode('signup');
                    setErrorMessage(null);
                  }}
                  className={`flex-1 py-2 rounded-xl text-xs font-bold font-mono transition flex items-center justify-center gap-2 ${
                    authMode === 'signup'
                      ? 'bg-gradient-to-r from-indigo-600 to-cyan-500 text-white shadow-md shadow-cyan-600/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  <UserPlus className="w-3.5 h-3.5" /> Create Account
                </button>
              </div>

              {/* Header Title */}
              <div className="mb-6">
                <h2 className="text-xl sm:text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                  {authMode === 'signin' ? (
                    <>
                      <LogIn className="w-5 h-5 text-indigo-400" /> Log In to Safety Operations Center
                    </>
                  ) : (
                    <>
                      <UserPlus className="w-5 h-5 text-cyan-400" /> Create Account in Backend Database
                    </>
                  )}
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  {authMode === 'signin'
                    ? 'Authenticate your persona with HMAC-SHA256 verified credentials stored in SQLite database.'
                    : 'Register your account. Credentials and role are persisted directly in safety_engine.db.'}
                </p>
              </div>

              {/* Error & Success Notification Banners */}
              {errorMessage && (
                <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2 animate-fadeIn">
                  <AlertCircle className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  <span>{errorMessage}</span>
                </div>
              )}

              {successMessage && (
                <div className="mb-4 p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs flex items-center gap-2 animate-fadeIn">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                  <span>{successMessage}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Step 1: Role Selector */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <label className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300 flex items-center gap-2">
                      <Terminal className="w-3.5 h-3.5 text-cyan-400" /> Select User Persona & Access Role
                    </label>
                    <span className="text-[11px] text-slate-500 font-mono">
                      {authMode === 'signup' ? 'Profile to Store in DB' : 'Persona View'}
                    </span>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {personas.map((p) => {
                      const Icon = p.icon;
                      const isSelected = selectedRole === p.id;
                      return (
                        <div
                          key={p.id}
                          onClick={() => handlePersonaSelect(p.id)}
                          className={`p-4 rounded-2xl border transition-all cursor-pointer relative flex flex-col justify-between ${
                            isSelected
                              ? 'bg-slate-900/90 border-indigo-500 shadow-lg shadow-indigo-500/20 ring-1 ring-indigo-500/50'
                              : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700 hover:bg-slate-900/40'
                          }`}
                        >
                          <div className="space-y-2">
                            <div className="flex items-center justify-between">
                              <div
                                className={`w-9 h-9 rounded-xl flex items-center justify-center ${
                                  isSelected ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                                }`}
                              >
                                <Icon className="w-5 h-5" />
                              </div>
                              <span className={`text-[10px] font-mono px-2 py-0.5 rounded border ${p.badgeColor}`}>
                                {p.badge}
                              </span>
                            </div>

                            <div className="font-bold text-sm text-white">{p.title}</div>
                            <p className="text-[11px] text-slate-400 leading-relaxed">{p.description}</p>
                          </div>

                          <div className="pt-3 mt-3 border-t border-slate-800/60 flex items-center justify-between text-[11px] font-mono">
                            <span className="text-slate-500">Preset Identity</span>
                            <span className={`font-semibold ${isSelected ? 'text-indigo-300' : 'text-slate-400'}`}>
                              {isSelected ? '✓ SELECTED' : 'Select'}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Step 2: Credentials Form */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2 border-t border-slate-800/60">
                  {/* Full Name */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
                      <User className="w-3.5 h-3.5 text-slate-400" /> Full Name / Identity
                    </label>
                    <input
                      type="text"
                      required
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      placeholder="e.g. Dhinesha Gnanavel"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-xs text-white font-mono placeholder-slate-600 outline-none transition"
                    />
                  </div>

                  {/* Email Address */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
                      <Building className="w-3.5 h-3.5 text-slate-400" /> Email Address
                    </label>
                    <input
                      type="email"
                      required
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="user@loopguard.ai"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-xs text-white font-mono placeholder-slate-600 outline-none transition"
                    />
                  </div>

                  {/* Password */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
                      <Lock className="w-3.5 h-3.5 text-slate-400" /> Password
                    </label>
                    <input
                      type="password"
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter password..."
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-xs text-white font-mono placeholder-slate-600 outline-none transition"
                    />
                  </div>

                  {/* Organization */}
                  <div className="space-y-1.5">
                    <label className="text-[11px] font-mono text-slate-400 flex items-center gap-1.5">
                      <Building className="w-3.5 h-3.5 text-slate-400" /> Department / College / Org
                    </label>
                    <input
                      type="text"
                      value={organization}
                      onChange={(e) => setOrganization(e.target.value)}
                      placeholder="Department of AI & Data Science"
                      className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900/80 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-xs text-white font-mono placeholder-slate-600 outline-none transition"
                    />
                  </div>
                </div>

                {/* Quick Demo Access Bar (Only on Sign In) */}
                {authMode === 'signin' && (
                  <div className="p-3 rounded-xl bg-[#080C14] border border-slate-800/80 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
                    <div className="flex items-center gap-2 text-slate-400 font-mono text-[11px]">
                      <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
                      <span>1-Click Persona Quick Fills:</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => handlePersonaSelect('student')}
                        className="text-[10px] font-mono px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                      >
                        ⚡ Student Auto-Fill
                      </button>
                      <button
                        type="button"
                        onClick={() => handlePersonaSelect('developer')}
                        className="text-[10px] font-mono px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                      >
                        ⚡ Dev Auto-Fill
                      </button>
                      <button
                        type="button"
                        onClick={() => handlePersonaSelect('security_lead')}
                        className="text-[10px] font-mono px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition"
                      >
                        ⚡ Security Admin
                      </button>
                    </div>
                  </div>
                )}

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isAuthenticating}
                  className="w-full py-3.5 px-6 rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-bold text-sm tracking-wide shadow-lg shadow-indigo-500/25 transition-all flex items-center justify-center gap-2 group disabled:opacity-50"
                >
                  {isAuthenticating ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>
                        {authMode === 'signup'
                          ? 'Creating Account in Backend Database...'
                          : 'Authenticating with Backend Database...'}
                      </span>
                    </>
                  ) : (
                    <>
                      <span>
                        {authMode === 'signup'
                          ? 'Create Account & Save to Backend Database'
                          : 'Log In & Enter Safety Operations Center'}
                      </span>
                      <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition" />
                    </>
                  )}
                </button>
              </form>

              {/* Switch link */}
              <div className="mt-5 text-center text-xs text-slate-400 font-mono">
                {authMode === 'signin' ? (
                  <span>
                    Don't have an account yet?{' '}
                    <button
                      type="button"
                      onClick={() => handleNavigateToAuth('signup')}
                      className="text-cyan-400 hover:text-cyan-300 font-bold underline ml-1"
                    >
                      Create Account
                    </button>
                  </span>
                ) : (
                  <span>
                    Already registered?{' '}
                    <button
                      type="button"
                      onClick={() => handleNavigateToAuth('signin')}
                      className="text-indigo-400 hover:text-indigo-300 font-bold underline ml-1"
                    >
                      Log In here
                    </button>
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Bottom Footer Metadata */}
      <footer className="w-full border-t border-slate-800/80 py-4 text-center text-[11px] font-mono text-slate-500 bg-[#070A12]/80">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <span>LoopGuard v1.0 &bull; Backend Native Database (safety_engine.db)</span>
          <span>Compliance: SOC 2 &bull; ISO 27001 &bull; SQLite Persistent Vault</span>
        </div>
      </footer>
    </div>
  );
};
