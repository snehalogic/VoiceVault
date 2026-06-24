export default function Verdict({ label, confidence }) {
  const isReal = label === "bonafide";
  const percent = (confidence * 100).toFixed(1);

  return (
    <div className={`rounded-xl p-6 flex flex-col items-center gap-4 border
      ${isReal
        ? "bg-green-950/40 border-green-600"
        : "bg-red-950/40 border-red-600"
      }`}
    >
      {/* Big verdict badge */}
      <div className={`text-4xl font-bold tracking-wide
        ${isReal ? "text-green-400" : "text-red-400"}`}
      >
        {isReal ? "✓ REAL" : "✗ FAKE"}
      </div>

      <div className="text-gray-300 text-sm">
        {isReal
          ? "This voice appears to be genuine human speech."
          : "This voice shows signs of AI generation or voice cloning."}
      </div>

      {/* Confidence bar */}
      <div className="w-full">
        <div className="flex justify-between text-xs text-gray-400 mb-1">
          <span>Confidence</span>
          <span>{percent}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-3">
          <div
            className={`h-3 rounded-full transition-all duration-700
              ${isReal ? "bg-green-500" : "bg-red-500"}`}
            style={{ width: `${percent}%` }}
          />
        </div>
      </div>
    </div>
  );
}