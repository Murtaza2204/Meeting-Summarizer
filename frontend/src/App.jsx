import { useEffect, useMemo, useRef, useState } from 'react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000';

const initialResult = {
  transcript: '',
  summary: '',
  language: '',
  requestId: '',
  model: '',
  mode: '',
};

function formatBytes(bytes) {
  if (!bytes && bytes !== 0) return '';
  const units = ['B', 'KB', 'MB', 'GB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }

  return `${value.toFixed(value >= 10 || unitIndex === 0 ? 0 : 1)} ${units[unitIndex]}`;
}

function App() {
  const fileInputRef = useRef(null);
  const [apiStatus, setApiStatus] = useState('checking');
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [transcriptInput, setTranscriptInput] = useState('');
  const [result, setResult] = useState(initialResult);

  const hasResult = Boolean(result.transcript || result.summary);

  useEffect(() => {
    let cancelled = false;

    async function checkHealth() {
      try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!cancelled) {
          setApiStatus(response.ok ? 'healthy' : 'error');
        }
      } catch {
        if (!cancelled) {
          setApiStatus('offline');
        }
      }
    }

    checkHealth();
    return () => {
      cancelled = true;
    };
  }, []);

  const statusLabel = useMemo(() => {
    switch (apiStatus) {
      case 'healthy':
        return 'API connected';
      case 'offline':
        return 'API offline';
      case 'error':
        return 'API error';
      default:
        return 'Checking API';
    }
  }, [apiStatus]);

  function resetOutput() {
    setError('');
    setResult(initialResult);
  }

  function pickFile(file) {
    if (!file) return;
    setSelectedFile(file);
    setError('');
    setResult(initialResult);
    setTranscriptInput('');
  }

  function onInputChange(event) {
    pickFile(event.target.files?.[0]);
  }

  function onDragOver(event) {
    event.preventDefault();
    setDragActive(true);
  }

  function onDragLeave() {
    setDragActive(false);
  }

  function onDrop(event) {
    event.preventDefault();
    setDragActive(false);
    pickFile(event.dataTransfer.files?.[0]);
  }

  async function sendAudio(endpoint) {
    if (!selectedFile) {
      setError('Please choose an audio file first.');
      return;
    }

    const formData = new FormData();
    formData.append('audio', selectedFile);

    setLoading(true);
    setError('');
    setResult(initialResult);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        body: formData,
      });

      const payload = await response.json();

      if (!response.ok || payload.success === false) {
        throw new Error(payload.error || 'Request failed.');
      }

      setResult({
        transcript: payload.transcript || '',
        summary: payload.summary || '',
        language: payload.language || '',
        requestId: payload.request_id || '',
        model: payload.model || '',
        mode: payload.mode || '',
      });

      if (payload.transcript) {
        setTranscriptInput(payload.transcript);
      }
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  async function summarizeTranscript() {
    const transcript = transcriptInput.trim();
    if (!transcript) {
      setError('Paste or generate a transcript first.');
      return;
    }

    setLoading(true);
    setError('');
    setResult((current) => ({ ...current, summary: '' }));

    try {
      const response = await fetch(`${API_BASE_URL}/summarize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ transcript }),
      });

      const payload = await response.json();

      if (!response.ok || payload.success === false) {
        throw new Error(payload.error || 'Summary request failed.');
      }

      setResult((current) => ({
        ...current,
        summary: payload.summary || '',
      }));
    } catch (err) {
      setError(err.message || 'Something went wrong.');
    } finally {
      setLoading(false);
    }
  }

  const clearAll = () => {
    setSelectedFile(null);
    setTranscriptInput('');
    setError('');
    setLoading(false);
    setResult(initialResult);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="page-shell">
      <div className="background-glow glow-one" />
      <div className="background-glow glow-two" />

      <main className="layout">
        <section className="hero">
          <div className="eyebrow">
            <span className={`status-dot ${apiStatus}`} />
            <span>{statusLabel}</span>
          </div>
          <h1>Turn meeting audio into English notes, fast.</h1>
          <p className="hero-copy">
            Upload a recording, let Sarvam translate it into English, then generate a concise
            summary and action items in one flow.
          </p>

          <div className="hero-stats">
            <div className="stat-card">
              <strong>Sarvam</strong>
              <span>English translation enabled</span>
            </div>
            <div className="stat-card">
              <strong>Flask API</strong>
              <span>Transcribe, summarize, or do both</span>
            </div>
            <div className="stat-card">
              <strong>Flexible input</strong>
              <span>Drop audio or paste transcript text</span>
            </div>
          </div>
        </section>

        <section className="workspace">
          <div className="panel upload-panel">
            <div
              className={`dropzone ${dragActive ? 'active' : ''}`}
              onDragOver={onDragOver}
              onDragLeave={onDragLeave}
              onDrop={onDrop}
            >
              <input
                ref={fileInputRef}
                className="file-input"
                type="file"
                accept=".mp3,.wav,.m4a,.flac,.ogg,.mp4"
                onChange={onInputChange}
              />
              <div className="dropzone-copy">
                <span className="dropzone-badge">Audio upload</span>
                <h2>Drop a meeting recording here</h2>
                <p>MP3, WAV, M4A, FLAC, OGG, and MP4 are supported.</p>
                <button type="button" className="secondary-button" onClick={() => fileInputRef.current?.click()}>
                  Choose file
                </button>
              </div>
            </div>

            <div className="file-row">
              <div>
                <p className="field-label">Selected file</p>
                <p className="file-name">{selectedFile ? selectedFile.name : 'No file chosen yet'}</p>
              </div>
              <div className="file-meta">
                {selectedFile ? formatBytes(selectedFile.size) : '0 B'}
              </div>
            </div>

            <div className="action-row">
              <button
                type="button"
                className="primary-button"
                onClick={() => sendAudio('/process')}
                disabled={loading}
              >
                {loading ? 'Working...' : 'Transcribe + Summarize'}
              </button>
              <button
                type="button"
                className="ghost-button"
                onClick={() => sendAudio('/transcribe')}
                disabled={loading}
              >
                Transcribe only
              </button>
              <button type="button" className="text-button" onClick={clearAll} disabled={loading}>
                Clear
              </button>
            </div>

            {error ? <div className="error-banner">{error}</div> : null}
          </div>

          <div className="panel transcript-panel">
            <div className="panel-heading">
              <div>
                <p className="field-label">Transcript</p>
                <h2>English transcript editor</h2>
              </div>
              <span className="inline-chip">{result.mode || 'translate'}</span>
            </div>
            <textarea
              value={transcriptInput}
              onChange={(event) => setTranscriptInput(event.target.value)}
              placeholder="Your English transcript will appear here after upload. You can also paste one manually and summarize it."
            />
            <div className="action-row compact">
              <button
                type="button"
                className="primary-button"
                onClick={summarizeTranscript}
                disabled={loading}
              >
                {loading ? 'Summarizing...' : 'Summarize transcript'}
              </button>
            </div>
          </div>

          <div className="panel output-panel">
            <div className="panel-heading">
              <div>
                <p className="field-label">Results</p>
                <h2>Meeting output</h2>
              </div>
              <div className="meta-stack">
                {result.language ? <span className="inline-chip">{result.language}</span> : null}
                {result.requestId ? <span className="inline-chip subtle">ID: {result.requestId}</span> : null}
              </div>
            </div>

            <div className="result-block">
              <h3>Summary</h3>
              <p className={hasResult ? 'result-text' : 'placeholder'}>
                {result.summary || 'Your meeting summary will appear here after processing.'}
              </p>
            </div>

            <div className="result-block">
              <h3>Transcript preview</h3>
              <p className={hasResult ? 'result-text transcript-text' : 'placeholder'}>
                {result.transcript || 'Your transcript will appear here after transcription.'}
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
