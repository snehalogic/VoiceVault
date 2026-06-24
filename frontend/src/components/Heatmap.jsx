export default function Heatmap({ chunks }) {
  if (!chunks || chunks.length === 0) return null;

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-gray-300 font-medium text-sm uppercase tracking-widest">
        Per-chunk timeline
      </h3>

      {/* Chunk blocks */}
      <div className="flex flex-wrap gap-2">
        {chunks.map((chunk, idx) => {
          const isReal = chunk.label === "bonafide";
          const confidence = (chunk.confidence * 100).toFixed(0);

          return (
            <div
              key={idx}
              title={`Chunk ${idx + 1}: ${isReal ? "Real" : "Fake"} (${confidence}%)`}
              className={`relative group flex flex-col items-center justify-center
                rounded-lg w-14 h-14 text-xs font-semibold cursor-default
                transition-transform hover:scale-110
                ${isReal
                  ? "bg-green-700/60 border border-green-500 text-green-200"
                  : "bg-red-700/60 border border-red-500 text-red-200"
                }`}
            >
              <span className="text-lg">{isReal ? "✓" : "✗"}</span>
              <span className="text-[10px] opacity-70">{chunk.start_time}s</span>

              {/* Tooltip on hover */}
              <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2
                bg-gray-800 text-white text-xs rounded px-2 py-1 whitespace-nowrap
                opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none
                border border-gray-600 z-10">
                Chunk {idx + 1} · {isReal ? "Real" : "Fake"} · {confidence}%
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-xs text-gray-500 mt-1">
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-green-600 inline-block" />
          Real chunk
        </span>
        <span className="flex items-center gap-1">
          <span className="w-3 h-3 rounded bg-red-600 inline-block" />
          Fake chunk
        </span>
      </div>
    </div>
  );
}