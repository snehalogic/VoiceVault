import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Uploader from "../components/Uploader";
import Waveform from "../components/Waveform";
import Verdict from "../components/Verdict";
import Heatmap from "../components/Heatmap";
import ReportDownload from "../components/ReportDownload";

export default function Detector() {
  const navigate = useNavigate();

  const [audioFile, setAudioFile] = useState(null);   // File object
  const [audioURL,  setAudioURL]  = useState(null);   // blob URL for waveform
  const [result,    setResult]    = useState(null);   // API response
  const [loading,   setLoading]   = useState(false);
  const [error,     setError]     = useState(null);

  const handleFileSelected = (file) => {
    setAudioFile(file);
    setAudioURL(URL.createObjectURL(file));
    setResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!audioFile) return;
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const form = new FormData();
      form.append("file", audioFile);

      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body:   form,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ detail: "Server error" }));
        throw new Error(body.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setAudioFile(null);
    setAudioURL(null);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center px-4 py-10">

      {/* ── Top bar ── */}
      <div className="w-full max-w-3xl mb-8 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate("/")}
            className="text-gray-400 hover:text-white text-sm flex items-center gap-1 transition-colors"
          >
            ← Back
          </button>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              Voice<span className="text-indigo-400">Vault</span>
            </h1>
            <p className="text-gray-400 text-xs mt-0.5">
              Real-time deepfake voice detection · RawNet2
            </p>
          </div>
        </div>

        {audioFile && (
          <button
            onClick={handleReset}
            className="text-xs text-gray-500 hover:text-gray-300 border border-gray-700
                       hover:border-gray-500 px-3 py-1.5 rounded-lg transition-colors"
          >
            ✕ Clear
          </button>
        )}
      </div>

      <div className="w-full max-w-3xl bg-gray-900 rounded-2xl shadow-2xl p-8 flex flex-col gap-6">

        <Uploader onFileSelected={handleFileSelected} />

        {audioURL && (
          <Waveform audioURL={audioURL} chunks={result?.chunks ?? []} />
        )}

        {audioFile && (
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className={`
              w-full py-3 rounded-xl font-semibold text-lg transition-all duration-200
              ${loading
                ? "bg-indigo-900 text-indigo-400 cursor-wait"
                : "bg-indigo-600 hover:bg-indigo-500 active:scale-[0.99] text-white"
              }
            `}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg"
                     fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10"
                          stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                Analyzing…
              </span>
            ) : "Analyze Voice"}
          </button>
        )}

        {/* Error state */}
        {error && (
          <div className="bg-red-950/60 border border-red-700 rounded-xl p-4 text-red-300 text-sm">
            <span className="font-semibold">Error: </span>{error}
          </div>
        )}

        {result && (
          <>
            {/* Verdict badge */}
            <Verdict label={result.verdict} confidence={result.confidence} />

            {/* Grad-CAM heatmap */}
            <Heatmap chunks={result.chunks} />

            {/* Divider */}
            <div className="border-t border-gray-800" />

            {/* PDF export */}
            <div className="flex flex-col gap-1">
              <p className="text-xs text-gray-500 uppercase tracking-widest font-semibold">
                Export
              </p>
              <ReportDownload file={audioFile} disabled={loading} />
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <p className="mt-8 text-gray-600 text-xs">
        Powered by RawNet2 · ASVspoof 2019 LA · AUC 0.9929
      </p>
    </div>
  );
}