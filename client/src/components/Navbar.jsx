import React from 'react';

export default function Navbar({ onReset, currentStep }) {
  return (
    <header style={{ background: '#fff', borderBottom: '1px solid #E5E7EB' }} className="sticky top-0 z-10">
      <div className="max-w-2xl mx-auto px-5 h-14 flex items-center justify-between">
        <div onClick={onReset} className="flex items-center gap-2.5 cursor-pointer select-none">
          <div style={{ background: 'linear-gradient(135deg, #F97316, #EA580C)', borderRadius: 8, width: 28, height: 28, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
          </div>
          <span className="font-semibold text-[15px] text-gray-900 tracking-tight">PrepGenie</span>
          <span style={{ fontSize: 11, fontWeight: 500, background: '#FFF7ED', color: '#EA580C', border: '1px solid #FED7AA', borderRadius: 99, padding: '1px 8px' }}>AI</span>
        </div>

        {currentStep !== 'upload' && (
          <button onClick={onReset} className="btn btn-ghost" style={{ padding: '6px 14px', fontSize: 13 }}>
            New Session
          </button>
        )}
      </div>
    </header>
  );
}
