import React from 'react';

interface LogoProps {
  className?: string;
  showBadge?: boolean;
}

export const Logo: React.FC<LogoProps> = ({ className = '', showBadge = true }) => {
  return (
    <div className={`flex items-center gap-2.5 font-sans select-none ${className}`}>
      <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-slate-900 text-cyan-400 shadow-md">
        <svg className="w-6 h-6" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M 8 34 C 16 30, 22 28, 22 12 C 22 12, 12 14, 8 20 Z" fill="currentColor" opacity="0.6" />
          <path d="M 36 34 C 28 30, 22 28, 22 12 C 22 12, 32 14, 36 20 Z" fill="currentColor" />
          <path d="M 22 12 L 22 36" stroke="#38BDF8" strokeWidth="3" strokeLinecap="round" />
          <circle cx="22" cy="12" r="3.5" fill="#10B981" />
          <circle cx="11" cy="20" r="2.5" fill="#38BDF8" />
          <circle cx="33" cy="20" r="2.5" fill="#10B981" />
        </svg>
      </div>
      <div className="flex items-center gap-1.5">
        <span className="text-xl font-extrabold tracking-tight text-slate-900 dark:text-white">
          Cogni<span className="text-transparent bg-clip-text bg-gradient-to-r from-sky-500 to-emerald-500">Learn</span>
        </span>
        {showBadge && (
          <span className="px-1.5 py-0.5 text-[10px] font-mono font-bold uppercase rounded bg-sky-500/10 text-sky-600 dark:text-sky-400 border border-sky-500/20">
            AI
          </span>
        )}
      </div>
    </div>
  );
};