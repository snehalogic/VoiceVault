
import { useState } from "react";

export default function Heatmap({ chunks = [] }) {
  const [selectedChunk, setSelectedChunk] = useState(0);

  const chunksWithCam = chunks.filter((c) => c.gradcam_image);

  if (chunksWithCam.length === 0) {
    return (
      <div className="rounded-xl border border-gray-700 bg-gray-900 p-6 text-center text-gray-500 text-sm">
        No Grad-CAM data available.
      </div>
    );
  }

  const active = chunksWithCam[selectedChunk] ?? chunksWithCam[0];
  const isSpoof = active.label === "spoof";

  return (
    <div className="rounded-xl border border-gray-700 bg-gray-900 p-4 space-y-4">
      {/* ── Header ── */}
      <div className="flex items-center justify-between">
        <h3 className="text-white font-semibold text-sm tracking-wide">
          🔬 Grad-CAM Explainability
        </h3>
        <span className="text-gray-400 text-xs">
          Showing chunk {selectedChunk + 1} / {chunksWithCam.length}
        </span>
      </div>

      {/* ── Chunk selector pills ── */}
      {chunksWithCam.length > 1 && (
        <div className="flex flex-wrap gap-2">
          {chunksWithCam.map((chunk, i) => {
            const spoof = chunk.label === "spoof";
            const active = i === selectedChunk;
            return (
              <button
                key={i}
                onClick={() => setSelectedChunk(i)}
                className={`
                  px-3 py-1 rounded-full text-xs font-medium border transition-all
                  ${active
                    ? spoof
                      ? "bg-red-600 border-red-500 text-white"
                      : "bg-green-600 border-green-500 text-white"
                    : spoof
                    ? "border-red-800 text-red-400 hover:bg-red-900/40"
                    : "border-green-800 text-green-400 hover:bg-green-900/40"
                  }
                `}
              >
                {chunk.start_time}s – {chunk.end_time}s
                <span className="ml-1 opacity-75">
                  ({Math.round(chunk.confidence * 100)}%)
                </span>
              </button>
            );
          })}
        </div>
      )}

      {/* ── Grad-CAM image ── */}
      <div className="rounded-lg overflow-hidden border border-gray-700">
        <img
          src={`data:image/png;base64,${active.gradcam_image}`}
          alt={`Grad-CAM chunk ${selectedChunk + 1}`}
          className="w-full object-contain"
          style={{ background: "#0f1117" }}
        />
      </div>

      {/* ── Interpretation hint ── */}
      <div
        className={`
          rounded-lg p-3 text-xs leading-relaxed
          ${isSpoof
            ? "bg-red-950/50 border border-red-800 text-red-300"
            : "bg-green-950/50 border border-green-800 text-green-300"
          }
        `}
      >
        {isSpoof ? (
          <>
            <span className="font-semibold">Red regions</span> show where the
            model detected synthetic artefacts. AI vocoders typically over-smooth
            the <span className="font-semibold">4–8 kHz band</span>, produce
            periodic phase glitches at frame boundaries (~10 ms), and generate
            unnaturally uniform formant transitions — all visible as warm colours
            in the overlay.
          </>
        ) : (
          <>
            <span className="font-semibold">Low uniform activation</span> across
            the spectrogram indicates natural speech patterns with no vocoder
            artefacts detected.
          </>
        )}
      </div>

      {/* ── Legend ── */}
      <div className="flex items-center gap-3 text-xs text-gray-400">
        <span className="font-medium text-gray-300">Activation scale:</span>
        <div className="flex items-center gap-1">
          <span
            className="inline-block w-16 h-3 rounded"
            style={{
              background:
                "linear-gradient(to right, #00008b, #0000ff, #00ffff, #00ff00, #ffff00, #ff0000)",
            }}
          />
        </div>
        <span>Low → High</span>
      </div>
    </div>
  );
}