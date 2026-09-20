import React from 'react';
import ScoreGauge from './ScoreGauge';

export default function EvaluationCard({ evaluation, onNextQuestion, onFinishInterview }) {
  if (!evaluation) return null;

  return (
    <div className="card" style={{ overflow: 'hidden', boxShadow: '0 4px 16px rgba(249,115,22,0.10)' }}>
      {/* Orange header */}
      <div style={{ background: 'linear-gradient(135deg, #F97316, #EA580C)', padding: '16px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ color: '#fff', fontWeight: 600, fontSize: 15 }}>Answer Evaluation</span>
        <span style={{ background: 'rgba(255,255,255,0.2)', color: '#fff', borderRadius: 99, padding: '3px 14px', fontSize: 14, fontWeight: 700 }}>
          {evaluation.overallScore} / 10
        </span>
      </div>

      <div style={{ padding: '24px' }}>
        {/* Score bars */}
        <div style={{ padding: '16px 20px', background: '#FAFAFA', borderRadius: 10, border: '1px solid #F3F4F6', marginBottom: 24, display: 'flex', flexDirection: 'column', gap: 14 }}>
          <ScoreGauge score={evaluation.technicalScore} label="Technical Accuracy" />
          <ScoreGauge score={evaluation.communicationScore} label="Communication" />
          <ScoreGauge score={evaluation.problemSolvingScore} label="Problem Solving" />
        </div>

        {/* Feedback */}
        <div style={{ marginBottom: 24 }}>
          <p style={{ fontSize: 11, fontWeight: 600, color: '#9CA3AF', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 8 }}>Feedback</p>
          <p style={{ fontSize: 13, color: '#374151', lineHeight: 1.7, padding: '12px 14px', background: '#FAFAFA', borderRadius: 8, border: '1px solid #F3F4F6' }}>
            {evaluation.feedback}
          </p>
        </div>

        {/* Strengths & Weaknesses */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 24 }}>
          {evaluation.strengths?.length > 0 && (
            <div style={{ padding: '14px 16px', background: '#F0FDF4', border: '1px solid #BBF7D0', borderRadius: 10 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: '#15803D', textTransform: 'uppercase', marginBottom: 10 }}>Strengths</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {evaluation.strengths.map((s, i) => <p key={i} style={{ fontSize: 12, color: '#166534', lineHeight: 1.5 }}>• {s}</p>)}
              </div>
            </div>
          )}
          {evaluation.weaknesses?.length > 0 && (
            <div style={{ padding: '14px 16px', background: '#FFFBEB', border: '1px solid #FDE68A', borderRadius: 10 }}>
              <p style={{ fontSize: 11, fontWeight: 600, color: '#B45309', textTransform: 'uppercase', marginBottom: 10 }}>Improve</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {evaluation.weaknesses.map((w, i) => <p key={i} style={{ fontSize: 12, color: '#92400E', lineHeight: 1.5 }}>• {w}</p>)}
              </div>
            </div>
          )}
        </div>

        {evaluation.followUpSuggestion && (
          <div style={{ padding: '10px 14px', background: '#FFF7ED', border: '1px solid #FED7AA', borderRadius: 8, fontSize: 12, color: '#9A3412', marginBottom: 24 }}>
            <strong>Note: </strong>{evaluation.followUpSuggestion}
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, paddingTop: 16, borderTop: '1px solid #F3F4F6' }}>
          <button onClick={onFinishInterview} className="btn btn-ghost" style={{ padding: '8px 16px' }}>Generate Report</button>
          <button onClick={onNextQuestion} className="btn btn-primary" style={{ padding: '8px 18px' }}>Next Question →</button>
        </div>
      </div>
    </div>
  );
}
