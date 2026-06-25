import { useState } from "react";

export default function ReportDownload({ file, disabled }) {
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleDownload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);

    try {
      const form = new FormData();
      form.append("file", file);

      const res = await fetch("http://localhost:8000/report", {
        method: "POST",
        body:   form,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: "Unknown error" }));
        throw new Error(err.detail || `HTTP ${res.status}`);
      }

      const blob        = await res.blob();
      const url         = URL.createObjectURL(blob);
      const a           = document.createElement("a");
      const safeName    = file.name.replace(/\.[^.]+$/, "");
      a.href            = url;
      a.download        = `voicevault_report_${safeName}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-start gap-2">
      <button
        onClick={handleDownload}
        disabled={disabled || loading || !file}
        className={`
          flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold text-sm
          transition-all duration-200 border
          ${disabled || !file
            ? "bg-gray-800 border-gray-700 text-gray-500 cursor-not-allowed"
            : loading
            ? "bg-indigo-900 border-indigo-700 text-indigo-300 cursor-wait"
            : "bg-indigo-700 border-indigo-500 text-white hover:bg-indigo-600 active:scale-95"
          }
        `}
      >
        {loading ? (
          <>
            {/* Spinner */}
            <svg className="animate-spin h-4 w-4 text-indigo-300"
                 xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10"
                      stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z" />
            </svg>
            Generating PDF…
          </>
        ) : (
          <>
            {/* Download icon */}
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4"
                 fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round"
                    d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2
                       M7 10l5 5 5-5
                       M12 3v12" />
            </svg>
            Download PDF Report
          </>
        )}
      </button>

      {error && (
        <p className="text-red-400 text-xs">
          ⚠ {error}
        </p>
      )}

      <p className="text-gray-500 text-xs">
        Includes verdict, all Grad-CAM heatmaps, and methodology
      </p>
    </div>
  );
}