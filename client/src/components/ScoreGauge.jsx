import React from 'react';

export default function ScoreGauge({ score = 0, maxScore = 10, label = '' }) {
  const pct = Math.min(100, Math.round((score / maxScore) * 100));
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 5, width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 12 }}>
        <span style={{ color: '#374151', fontWeight: 500 }}>{label}</span>
        <span style={{ fontWeight: 600, color: pct >= 70 ? '#15803D' : pct >= 45 ? '#B45309' : '#DC2626', fontSize: 12 }}>{score}/{maxScore}</span>
      </div>
      <div className="score-track">
        <div className="score-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
