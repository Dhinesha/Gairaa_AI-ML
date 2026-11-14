import React from 'react';
import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../context/ThemeContext';

interface ThemeToggleProps {
  variant?: 'compact' | 'pill' | 'expanded';
  className?: string;
}

export const ThemeToggle: React.FC<ThemeToggleProps> = ({
  variant = 'compact',
  className = '',
}) => {
  const { theme, toggleTheme } = useTheme();
  const isLight = theme === 'light';

  if (variant === 'pill') {
    return (
      <button
        type="button"
        id="theme-toggle-pill-btn"
        onClick={toggleTheme}
        className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-mono font-medium transition-all shadow-sm ${
          isLight
            ? 'bg-white border-slate-300 text-slate-800 hover:bg-slate-100 shadow-slate-200'
            : 'bg-slate-900/90 border-slate-700 text-slate-200 hover:bg-slate-800 hover:border-slate-600'
        } ${className}`}
        title={isLight ? 'Switch to Cyber Dark Mode' : 'Switch to Mild White/Grey Clean Mode'}
        aria-label="Toggle platform color theme"
      >
        <div
          className={`w-5 h-5 rounded-full flex items-center justify-center transition-colors ${
            isLight ? 'bg-amber-100 text-amber-600' : 'bg-cyan-500/20 text-cyan-400'
          }`}
        >
          {isLight ? <Sun className="w-3.5 h-3.5" /> : <Moon className="w-3.5 h-3.5" />}
        </div>
        <span className="hidden sm:inline">
          {isLight ? 'Mild Slate' : 'Cyber Dark'}
        </span>
      </button>
    );
  }

  if (variant === 'expanded') {
    return (
      <div
        className={`flex items-center p-1 rounded-2xl border transition-all ${
          isLight
            ? 'bg-slate-100 border-slate-200'
            : 'bg-slate-900/90 border-slate-800'
        } ${className}`}
      >
        <button
          type="button"
          onClick={() => isLight && toggleTheme()}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium font-mono transition-all ${
            !isLight
              ? 'bg-slate-800 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/20'
              : 'text-slate-500 hover:text-slate-700'
          }`}
        >
          <Moon className="w-3.5 h-3.5" />
          <span>Cyber Dark</span>
        </button>
        <button
          type="button"
          onClick={() => !isLight && toggleTheme()}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-medium font-mono transition-all ${
            isLight
              ? 'bg-white text-amber-600 border border-amber-300/60 shadow-sm shadow-amber-500/20'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          <Sun className="w-3.5 h-3.5" />
          <span>Mild White/Grey</span>
        </button>
      </div>
    );
  }

  // Default compact button
  return (
    <button
      type="button"
      id="theme-toggle-btn"
      onClick={toggleTheme}
      className={`p-2 rounded-xl border transition-all flex items-center justify-center ${
        isLight
          ? 'bg-white border-slate-300 text-amber-600 hover:bg-slate-100 shadow-sm hover:border-amber-400'
          : 'bg-slate-900/90 border-slate-700 text-cyan-400 hover:bg-slate-800 hover:border-cyan-500/50'
      } ${className}`}
      title={isLight ? 'Switch to Cyber Dark Mode' : 'Switch to Mild White/Grey Clean Mode'}
      aria-label="Toggle color theme"
    >
      {isLight ? (
        <Sun className="w-4 h-4 text-amber-500 transition-transform duration-300 rotate-0 hover:rotate-90" />
      ) : (
        <Moon className="w-4 h-4 text-cyan-400 transition-transform duration-300 -rotate-12 hover:rotate-0" />
      )}
    </button>
  );
};

