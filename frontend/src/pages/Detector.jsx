import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Uploader from "../components/Uploader";
import Waveform from "../components/Waveform";
import Verdict from "../components/Verdict";
import Heatmap from "../components/Heatmap";

export default function Detector() {
  const navigate = useNavigate();
  const [audioFile, setAudioFile] = useState(null);
  const [audioURL, setAudioURL] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
      const formData = new FormData();
      formData.append("file", audioFile);

      const response = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col items-center px-4 py-12">

      {/* Back button + header */}
      <div className="w-full max-w-3xl mb-8 flex items-center gap-4">
        <button
          onClick={() => navigate("/")}
          className="text-gray-400 hover:text-white text-sm flex items-center gap-1 transition-colors"
        >
          ← Back
        </button>
        <div>
          <h1 className="text-3xl font-bold">
            Voice<span className="text-indigo-400">Vault</span>
          </h1>
          <p className="text-gray-400 text-sm">Real-time deepfake voice detection</p>
        </div>
      </div>

      {/* Main card */}
      <div className="w-full max-w-3xl bg-gray-900 rounded-2xl shadow-2xl p-8 flex flex-col gap-6">

        <Uploader onFileSelected={handleFileSelected} />

        {audioURL && (
          <Waveform audioURL={audioURL} chunks={result?.chunks} />
        )}

        {audioFile && (
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full py-3 rounded-xl font-semibold text-lg transition-all
              bg-indigo-600 hover:bg-indigo-500 disabled:bg-indigo-900
              disabled:cursor-not-allowed"
          >
            {loading ? "Analyzing..." : "Analyze Voice"}
          </button>
        )}

        {error && (
          <div className="bg-red-900/40 border border-red-600 rounded-xl p-4 text-red-300">
            {error}
          </div>
        )}

        {result && (
          <>
            <Verdict label={result.verdict} confidence={result.confidence} />
            <Heatmap chunks={result.chunks} />
          </>
        )}
      </div>

      <p className="mt-8 text-gray-600 text-sm">
        Powered by RawNet2 · ASVspoof 2019 LA
      </p>
    </div>
  );
}