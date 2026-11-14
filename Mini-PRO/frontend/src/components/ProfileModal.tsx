import React from 'react';
import {
  X,
  User,
  GraduationCap,
  Code2,
  ShieldCheck,
  LogOut,
  Sliders,
  CheckCircle2,
  Clock,
  Building,
  Mail,
  KeyRound,
  ShieldAlert,
} from 'lucide-react';
import { UserProfile } from '../types';
import { ThemeToggle } from './ThemeToggle';

interface ProfileModalProps {
  user: UserProfile;
  isOpen: boolean;
  onClose: () => void;
  onUpdateUser: (updated: UserProfile) => void;
  onSignOut: () => void;
}

export const ProfileModal: React.FC<ProfileModalProps> = ({
  user,
  isOpen,
  onClose,
  onUpdateUser,
  onSignOut,
}) => {
  if (!isOpen) return null;

  const roles = [
    {
      id: 'student' as const,
      name: 'Student / Researcher',
      icon: GraduationCap,
      badge: 'Academic Mode',
      color: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
      description: 'Optimized for learning loop detection algorithms and exporting thesis reports.',
    },
    {
      id: 'developer' as const,
      name: 'Software Developer',
      icon: Code2,
      badge: 'Engineering Mode',
      color: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/20',
      description: 'Focus on raw SHA-256 hashes, MCP tool calls, and API debugging.',
    },
    {
      id: 'security_lead' as const,
      name: 'Security Architect',
      icon: ShieldCheck,
      badge: 'Governance Mode',
      color: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      description: 'Full administrative access for Human-in-the-Loop sensitive approvals.',
    },
  ];

  const handleRoleChange = (role: 'student' | 'developer' | 'security_lead') => {
    const updated: UserProfile = {
      ...user,
      role,
      studentModeEnabled: role === 'student',
    };
    onUpdateUser(updated);
  };

  const handleToggleStudentMode = () => {
    const updated: UserProfile = {
      ...user,
      studentModeEnabled: !user.studentModeEnabled,
    };
    onUpdateUser(updated);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-md animate-fadeIn select-none">
      <div className="w-full max-w-xl glass-panel bg-[#0B0F19] border border-slate-800 rounded-3xl shadow-2xl overflow-hidden relative">
        {/* Top Header */}
        <div className="p-6 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-12 h-12 rounded-2xl bg-gradient-to-tr ${user.avatarColor} p-[1px] shadow-lg`}>
              <div className="w-full h-full bg-[#0B0F19] rounded-2xl flex items-center justify-center">
                {user.role === 'student' ? (
                  <GraduationCap className="w-6 h-6 text-emerald-400" />
                ) : user.role === 'developer' ? (
                  <Code2 className="w-6 h-6 text-cyan-400" />
                ) : (
                  <ShieldCheck className="w-6 h-6 text-purple-400" />
                )}
              </div>
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-2">
                {user.name}
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                  Online
                </span>
              </h2>
              <p className="text-xs text-slate-400 flex items-center gap-2 font-mono">
                <span>{user.email}</span> &bull; <span>Logged in {user.loginTime}</span>
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-xl bg-slate-800/60 hover:bg-slate-700 text-slate-400 hover:text-white flex items-center justify-center transition"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-6 max-h-[75vh] overflow-y-auto">
          {/* Identity & Org Info */}
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-500 flex items-center gap-1 mb-1">
                <Building className="w-3 h-3 text-slate-400" /> Organization / Dept
              </span>
              <span className="text-slate-200 font-medium truncate block">{user.organization}</span>
            </div>

            <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-mono uppercase text-slate-500 flex items-center gap-1 mb-1">
                <KeyRound className="w-3 h-3 text-slate-400" /> Security Clearance
              </span>
              <span className="text-emerald-400 font-mono font-bold block">LEVEL-3 (VERIFIED)</span>
            </div>
          </div>

          {/* Switch Persona Role */}
          <div className="space-y-3">
            <label className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-cyan-400" /> Active Profile & Persona
            </label>
            <p className="text-[11px] text-slate-400">
              Switch role view dynamically without re-logging in:
            </p>

            <div className="space-y-2">
              {roles.map((r) => {
                const Icon = r.icon;
                const isCurrent = user.role === r.id;
                return (
                  <div
                    key={r.id}
                    onClick={() => handleRoleChange(r.id)}
                    className={`p-3 rounded-xl border flex items-center justify-between cursor-pointer transition ${
                      isCurrent
                        ? 'bg-slate-900 border-indigo-500 ring-1 ring-indigo-500/50'
                        : 'bg-slate-950/40 border-slate-800/80 hover:border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                          isCurrent ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-white flex items-center gap-2">
                          {r.name}
                          <span className={`text-[9px] font-mono px-1.5 py-0.2 rounded border ${r.color}`}>
                            {r.badge}
                          </span>
                        </div>
                        <p className="text-[11px] text-slate-400">{r.description}</p>
                      </div>
                    </div>

                    <div className="text-xs font-mono">
                      {isCurrent ? (
                        <span className="text-indigo-400 font-bold flex items-center gap-1">
                          <CheckCircle2 className="w-4 h-4" /> Active
                        </span>
                      ) : (
                        <span className="text-slate-500 hover:text-slate-300">Switch</span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Profile Settings Toggles */}
          <div className="space-y-3 pt-3 border-t border-slate-800/80">
            <label className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300">
              Workspace Preferences
            </label>

            <div className="space-y-2">
              {/* Platform Theme Preference */}
              <div className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3 transition">
                <div>
                  <div className="text-xs font-bold text-white flex items-center gap-1.5">
                    Platform Theme & Color Mode
                  </div>
                  <p className="text-[11px] text-slate-400">
                    Switch between Mild Slate (White/Grey) and Cyber Deep Space Dark.
                  </p>
                </div>
                <ThemeToggle variant="expanded" />
              </div>

              <div
                onClick={handleToggleStudentMode}
                className="p-3 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between cursor-pointer hover:border-slate-700 transition"
              >
                <div>
                  <div className="text-xs font-bold text-white">Student Visual Tooltips & Explainer</div>
                  <p className="text-[11px] text-slate-400">
                    Display educational tooltips on flowchart nodes explaining cyclic loop math.
                  </p>
                </div>
                <div
                  className={`w-10 h-6 rounded-full transition-colors flex items-center px-1 ${
                    user.studentModeEnabled ? 'bg-indigo-600 justify-end' : 'bg-slate-700 justify-start'
                  }`}
                >
                  <div className="w-4 h-4 rounded-full bg-white shadow-md" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800/80 bg-slate-950/60 flex items-center justify-between">
          <button
            onClick={onSignOut}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 border border-rose-500/30 text-rose-300 text-xs font-semibold transition"
          >
            <LogOut className="w-3.5 h-3.5" /> Sign Out & Switch Account
          </button>

          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition"
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
};

