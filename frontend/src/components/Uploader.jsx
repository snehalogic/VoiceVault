import { useCallback, useState } from "react";

export default function Uploader({ onFileSelected }) {
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleFile = useCallback((file) => {
    if (!file) return;
    const validTypes = ["audio/wav", "audio/mpeg", "audio/flac", "audio/ogg", "audio/mp4", "audio/x-m4a"];
    const validExts = [".wav", ".mp3", ".flac", ".ogg", ".m4a"];
    const ext = "." + file.name.split(".").pop().toLowerCase();

    if (!validTypes.includes(file.type) && !validExts.includes(ext)) {
      alert("Please upload an audio file (.wav, .mp3, .flac, .ogg, .m4a)");
      return;
    }
    setFileName(file.name);
    onFileSelected(file);
  }, [onFileSelected]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  }, [handleFile]);

  const onInputChange = (e) => {
    handleFile(e.target.files[0]);
  };

  return (
    <div
      onDrop={onDrop}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      className={`border-2 border-dashed rounded-xl p-10 text-center transition-all cursor-pointer
        ${dragOver
          ? "border-indigo-400 bg-indigo-950/40"
          : "border-gray-700 hover:border-indigo-600 hover:bg-gray-800/40"
        }`}
      onClick={() => document.getElementById("audio-input").click()}
    >
      <input
        id="audio-input"
        type="file"
        accept=".wav,.mp3,.flac,.ogg,.m4a"
        className="hidden"
        onChange={onInputChange}
      />

      <div className="flex flex-col items-center gap-3">
        {/* Upload icon */}
        <svg className="w-12 h-12 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M12 16V4m0 0L8 8m4-4l4 4M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1" />
        </svg>

        {fileName ? (
          <div>
            <p className="text-indigo-300 font-medium">{fileName}</p>
            <p className="text-gray-500 text-sm mt-1">Click or drop to change file</p>
          </div>
        ) : (
          <div>
            <p className="text-gray-300 font-medium">Drop an audio file here</p>
            <p className="text-gray-500 text-sm mt-1">or click to browse · WAV, MP3, FLAC, OGG, M4A</p>
          </div>
        )}
      </div>
    </div>
  );
}