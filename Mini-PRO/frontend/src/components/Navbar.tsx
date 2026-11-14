import React, { useEffect, useState } from 'react';
import {
  ShieldAlert,
  PlayCircle,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Sliders,
  BarChart3,
  Layers,
  Server,
  GraduationCap,
  Code2,
  ShieldCheck,
  User,
} from 'lucide-react';
import { api } from '../services/api';
import { UserProfile } from '../types';
import { useTheme } from '../context/ThemeContext';
import { ThemeToggle } from './ThemeToggle';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  pendingApprovalsCount: number;
  user?: UserProfile | null;
  onOpenProfile?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  pendingApprovalsCount,
  user,
  onOpenProfile,
}) => {
  const { theme } = useTheme();
  const isLight = theme === 'light';
  const [engineHealth, setEngineHealth] = useState<{ status: string; db: boolean; redis: boolean } | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await api.getHealth();
        setEngineHealth({
          status: res.status,
          db: res.database_connected,
          redis: res.redis_connected,
        });
      } catch {
        setEngineHealth({ status: 'offline', db: false, redis: false });
      }
    };
    check();
    const interval = setInterval(check, 10000);
    return () => clearInterval(interval);
  }, []);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', shortLabel: 'Dashboard', icon: Activity },
    { id: 'create', label: 'New Workflow', shortLabel: 'New', icon: PlayCircle },
    { id: 'workflows', label: 'Workflows', shortLabel: 'Workflows', icon: Layers },
    { id: 'safety-events', label: 'Safety Events', shortLabel: 'Safety', icon: ShieldAlert },
    {
      id: 'approvals',
      label: 'Approvals',
      shortLabel: 'Approvals',
      icon: CheckCircle2,
      badge: pendingApprovalsCount > 0 ? pendingApprovalsCount : undefined,
    },
    { id: 'analytics', label: 'Analytics', shortLabel: 'Analytics', icon: BarChart3 },
    { id: 'configuration', label: 'Config', shortLabel: 'Config', icon: Sliders },
  ];

  return (
    <header
      className={`sticky top-0 z-50 transition-colors duration-200 border-b backdrop-blur-md ${
        isLight
          ? 'bg-white/90 border-slate-200 shadow-sm'
          : 'glass-panel border-slate-800 bg-[#0B0F19]/90'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand - Ultra-Compact Shield Icon Logo */}
        <div
          id="nav-brand-logo"
          title="LoopGuard Dashboard"
          className="flex items-center cursor-pointer flex-shrink-0 mr-3 sm:mr-5 select-none group"
          onClick={() => setActiveTab('dashboard')}
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-[1px] shadow-glow-cyan flex-shrink-0 transition-transform duration-200 group-hover:scale-105">
            <div
              className={`w-full h-full rounded-xl flex items-center justify-center transition-colors ${
                isLight ? 'bg-white' : 'bg-[#0B0F19]'
              }`}
            >
              <ShieldAlert className="w-5 h-5 text-indigo-600 dark:text-cyan-400" />
            </div>
          </div>
        </div>

        {/* Navigation Tabs - Clean, Responsive & Never Overlapping */}
        <nav className="flex items-center gap-1 sm:gap-1.5 flex-1 justify-center max-w-2xl px-1 sm:px-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                id={`nav-${item.id}`}
                onClick={() => setActiveTab(item.id)}
                title={item.label}
                className={`relative flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-sm shadow-indigo-500/30'
                    : isLight
                    ? 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className="w-4 h-4 flex-shrink-0" />
                <span className="hidden xl:inline">{item.label}</span>
                <span className="hidden md:inline xl:hidden">{item.shortLabel}</span>
                {item.badge !== undefined && (
                  <span className="ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold bg-amber-500 text-black animate-pulse leading-none">
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Engine Status indicator, Theme Switcher & User Profile - Fixed Width */}
        <div className={`flex items-center gap-2 sm:gap-2.5 pl-2 sm:pl-3 border-l text-xs flex-shrink-0 ${isLight ? 'border-slate-200' : 'border-slate-800'}`}>
          {/* Theme Switcher Toggle */}
          <ThemeToggle variant="compact" />

          {/* Engine Status */}
          <div className="hidden lg:flex items-center gap-2">
            <div
              className={`w-2 h-2 rounded-full ${
                engineHealth?.status === 'healthy' ? 'bg-emerald-500 live-indicator' : 'bg-amber-400'
              }`}
            />
            <span className={`font-mono text-[11px] ${isLight ? 'text-slate-600' : 'text-slate-300'}`}>
              {engineHealth?.status === 'healthy' ? 'SAFETY GATE ACTIVE' : 'ENGINE CONNECTING'}
            </span>
          </div>

          {/* User Profile & Persona Trigger */}
          {user && onOpenProfile && (
            <button
              id="user-profile-btn"
              onClick={onOpenProfile}
              className={`flex items-center gap-2 p-1.5 pl-2 pr-3 rounded-xl border transition group ${
                isLight
                  ? 'bg-slate-100 hover:bg-slate-200 border-slate-200 text-slate-800'
                  : 'bg-slate-900/80 hover:bg-slate-800 border-slate-800 text-white'
              }`}
              title="Open Profile & Settings"
            >
              <div className={`w-7 h-7 rounded-lg bg-gradient-to-tr ${user.avatarColor} p-[1px]`}>
                <div
                  className={`w-full h-full rounded-lg flex items-center justify-center ${
                    isLight ? 'bg-white' : 'bg-[#0B0F19]'
                  }`}
                >
                  {user.role === 'student' ? (
                    <GraduationCap className="w-3.5 h-3.5 text-emerald-500" />
                  ) : user.role === 'developer' ? (
                    <Code2 className="w-3.5 h-3.5 text-cyan-500" />
                  ) : (
                    <ShieldCheck className="w-3.5 h-3.5 text-purple-500" />
                  )}
                </div>
              </div>

              <div className="text-left hidden sm:block">
                <span className={`text-xs font-bold block leading-tight truncate max-w-[110px] ${isLight ? 'text-slate-900' : 'text-white'}`}>
                  {user.name.split(' ')[0]}
                </span>
                <span className={`text-[10px] font-mono uppercase block ${isLight ? 'text-slate-500' : 'text-slate-400'}`}>
                  {user.role === 'student' ? 'Student' : user.role === 'developer' ? 'Developer' : 'Sec Lead'}
                </span>
              </div>
            </button>
          )}
        </div>
      </div>
    </header>
  );
};
