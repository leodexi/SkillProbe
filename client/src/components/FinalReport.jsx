import React from 'react';
import ScoreGauge from './ScoreGauge';

export default function FinalReport({ reportData, onReset }) {
  if (!reportData) return null;

  return (
    <div style={{ padding: '24px 0 56px' }}>

      {/* Hero score card */}
      <div className="card" style={{ overflow: 'hidden', marginBottom: 20, boxShadow: '0 4px 20px rgba(249,115,22,0.12)' }}>
        <div style={{ background: 'linear-gradient(135deg, #F97316 0%, #EA580C 100%)', padding: '28px 28px 24px' }}>
          <p style={{ color: 'rgba(255,255,255,0.7)', fontSize: 12, fontWeight: 500, marginBottom: 6 }}>Overall Performance Score</p>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 6 }}>
            <span style={{ color: '#fff', fontSize: 48, fontWeight: 700, lineHeight: 1 }}>{reportData.overallScore}</span>
            <span style={{ color: 'rgba(255,255,255,0.55)', fontSize: 20 }}>/100</span>
          </div>
        </div>
        <div style={{ padding: '20px 28px', display: 'flex', flexDirection: 'column', gap: 14 }}>
          <ScoreGauge score={reportData.technicalScore} maxScore={100} label="Technical" />
          <ScoreGauge score={reportData.communicationScore} maxScore={100} label="Communication" />
          <ScoreGauge score={reportData.problemSolvingScore} maxScore={100} label="Problem Solving" />
        </div>
      </div>

      {/* Overall feedback */}
      <div className="card" style={{ padding: '20px 24px', marginBottom: 20 }}>
        <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>Overall Feedback</p>
        <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.75 }}>{reportData.overallFeedback}</p>
      </div>

      {/* Strong / Weak areas */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div className="card" style={{ padding: '18px 20px' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#15803D', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>Strong Areas</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {reportData.strongAreas?.length > 0
              ? reportData.strongAreas.map((a, i) => <p key={i} style={{ fontSize: 13, color: '#166534', lineHeight: 1.5 }}>• {a}</p>)
              : <p style={{ fontSize: 13, color: '#9CA3AF' }}>—</p>}
          </div>
        </div>
        <div className="card" style={{ padding: '18px 20px' }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#B45309', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12 }}>Needs Work</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {reportData.weakAreas?.length > 0
              ? reportData.weakAreas.map((a, i) => <p key={i} style={{ fontSize: 13, color: '#92400E', lineHeight: 1.5 }}>• {a}</p>)
              : <p style={{ fontSize: 13, color: '#9CA3AF' }}>—</p>}
          </div>
        </div>
      </div>

      {/* Recommended topics */}
      {reportData.recommendedLearning?.length > 0 && (
        <div className="card" style={{ padding: '20px 24px', marginBottom: 28 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 14 }}>Recommended Topics</p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
            {reportData.recommendedLearning.map((item, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', background: '#FAFAFA', border: '1px solid #F3F4F6', borderRadius: 8 }}>
                <span style={{ width: 22, height: 22, borderRadius: '50%', background: 'linear-gradient(135deg,#F97316,#EA580C)', color: '#fff', fontSize: 11, fontWeight: 700, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{i + 1}</span>
                <span style={{ fontSize: 13, color: '#374151', lineHeight: 1.4 }}>{item}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'center' }}>
        <button onClick={onReset} className="btn btn-primary" style={{ padding: '11px 32px', fontSize: 14 }}>Start New Interview</button>
      </div>
    </div>
  );
}
