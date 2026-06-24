import { useEffect, useRef } from "react";
import WaveSurfer from "wavesurfer.js";

export default function Waveform({ audioURL, chunks }) {
  const containerRef = useRef(null);
  const wavesurferRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current || !audioURL) return;

    if (wavesurferRef.current) {
      wavesurferRef.current.destroy();
    }

    wavesurferRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: "#6366f1",
      progressColor: "#a5b4fc",
      cursorColor: "#e0e7ff",
      barWidth: 2,
      barGap: 1,
      barRadius: 2,
      height: 80,
      normalize: true,
      backend: "WebAudio",
    });

    wavesurferRef.current.load(audioURL);

    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
      }
    };
  }, [audioURL]);

  const handlePlayPause = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause();
    }
  };

  return (
    <div className="flex flex-col gap-3">
      {/* Waveform display */}
      <div
        ref={containerRef}
        className="w-full rounded-xl bg-gray-800 px-3 py-2 cursor-pointer"
        onClick={handlePlayPause}
        title="Click to play/pause"
      />

      <p className="text-gray-500 text-xs text-center">
        Click waveform to play / pause
      </p>
    </div>
  );
}