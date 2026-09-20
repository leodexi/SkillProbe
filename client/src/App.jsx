import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadResume from './components/UploadResume';
import InterviewSession from './components/InterviewSession';
import FinalReport from './components/FinalReport';

const API = 'http://localhost:8000';

export default function App() {
  const [step, setStep] = useState('upload');
  const [interviewData, setInterviewData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [loadingReport, setLoadingReport] = useState(false);
  const [error, setError] = useState(null);

  const handleReset = () => {
    setStep('upload'); setInterviewData(null); setReportData(null); setError(null);
  };

  const handleGenerateReport = async (interviewId) => {
    setLoadingReport(true); setError(null);
    try {
      const res = await fetch(`${API}/api/interviews/${interviewId}/report`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Failed to generate report');
      setReportData(data); setStep('report');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoadingReport(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: '#FAFAFA', display: 'flex', flexDirection: 'column' }}>
      <Navbar onReset={handleReset} currentStep={step} />

      <main style={{ flex: 1, width: '100%', maxWidth: 672, margin: '0 auto', padding: '0 16px' }}>
        {loadingReport && (
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: 300, gap: 12 }}>
            <div className="spinner" style={{ color: '#F97316', width: 24, height: 24, borderWidth: 3 }} />
            <p style={{ fontSize: 14, fontWeight: 500, color: '#374151' }}>Generating your performance report...</p>
          </div>
        )}

        {!loadingReport && error && (
          <div style={{ margin: '40px auto', maxWidth: 400, padding: 16, background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 10, textAlign: 'center' }}>
            <p style={{ fontSize: 13, color: '#DC2626', marginBottom: 12 }}>{error}</p>
            <button onClick={() => setStep('interview')} className="btn btn-ghost" style={{ fontSize: 13 }}>Back</button>
          </div>
        )}

        {!loadingReport && !error && (
          <>
            {step === 'upload' && <UploadResume onUploadSuccess={(d) => { setInterviewData(d); setStep('interview'); }} />}
            {step === 'interview' && interviewData && <InterviewSession interviewData={interviewData} onGenerateReport={handleGenerateReport} />}
            {step === 'report' && reportData && <FinalReport reportData={reportData} onReset={handleReset} />}
          </>
        )}
      </main>
    </div>
  );
}
