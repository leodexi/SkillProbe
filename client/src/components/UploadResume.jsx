import React, { useState } from 'react';

const API = 'http://localhost:8000';

export default function UploadResume({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const onDrop = (e) => {
    e.preventDefault();
    const f = e.dataTransfer?.files[0] || e.target.files?.[0];
    if (!f) return;
    if (f.type !== 'application/pdf') return setError('Please upload a PDF file.');
    setFile(f); setError(null);
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true); setError(null);
    const form = new FormData();
    form.append('resume', file);
    try {
      const res = await fetch(`${API}/api/interviews/upload`, { method: 'POST', body: form });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Upload failed');
      onUploadSuccess(data);
    } catch (e) {
      setError(e.message || 'Failed to process resume. Try again.');
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 480, margin: '0 auto', padding: '40px 0' }}>
      {/* Header */}
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <div style={{ width: 48, height: 48, borderRadius: 14, background: 'linear-gradient(135deg, #F97316, #EA580C)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', boxShadow: '0 4px 14px rgba(249,115,22,0.35)' }}>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2" strokeLinecap="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        </div>
        <h1 style={{ fontSize: 22, fontWeight: 700, color: '#111827', letterSpacing: '-0.4px', marginBottom: 6 }}>AI Technical Interview</h1>
        <p style={{ fontSize: 14, color: '#6B7280' }}>Upload your resume to get personalized adaptive questions</p>
      </div>

      {/* Card */}
      <div className="card" style={{ padding: 24, boxShadow: '0 4px 20px rgba(249,115,22,0.08)' }}>
        {/* Dropzone */}
        <div
          onDrop={onDrop}
          onDragOver={e => e.preventDefault()}
          onClick={() => document.getElementById('pdf-input').click()}
          style={{
            border: `2px dashed ${file ? '#86EFAC' : '#D1D5DB'}`,
            borderRadius: 10, padding: '28px 20px', textAlign: 'center', cursor: 'pointer',
            background: file ? '#F7FEE7' : '#FAFAFA', transition: 'all 0.2s'
          }}
        >
          <input id="pdf-input" type="file" accept=".pdf" style={{ display: 'none' }} onChange={onDrop} />
          {file ? (
            <>
              <p style={{ fontWeight: 600, color: '#111827', fontSize: 14 }}>{file.name}</p>
              <p style={{ fontSize: 12, color: '#6B7280', marginTop: 4 }}>{(file.size / 1024 / 1024).toFixed(2)} MB • Click to replace</p>
            </>
          ) : (
            <>
              <p style={{ fontSize: 14, fontWeight: 500, color: '#374151' }}>Click to upload or drag & drop</p>
              <p style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>PDF only, max 10MB</p>
            </>
          )}
        </div>

        {error && <p style={{ fontSize: 12, color: '#DC2626', marginTop: 12, padding: '8px 12px', background: '#FEF2F2', border: '1px solid #FECACA', borderRadius: 8 }}>{error}</p>}

        <button onClick={handleUpload} disabled={!file || loading} className="btn btn-primary" style={{ width: '100%', marginTop: 16, padding: '10px 0', fontSize: 14 }}>
          {loading ? <><div className="spinner text-white" /><span>Processing Resume...</span></> : 'Start Interview →'}
        </button>
      </div>
    </div>
  );
}
