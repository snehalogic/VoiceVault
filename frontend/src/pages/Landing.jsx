import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">

      {/* Navbar */}
      <nav className="flex items-center justify-between px-8 py-5 border-b border-gray-800">
        <span className="text-xl font-bold">
          Voice<span className="text-indigo-400">Vault</span>
        </span>
        <button
          onClick={() => navigate("/detect")}
          className="px-5 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm font-semibold transition-all"
        >
          Try it now
        </button>
      </nav>

      {/* Hero */}
      <section className="flex flex-col items-center justify-center text-center px-6 py-24 gap-6">
        <div className="inline-block px-3 py-1 bg-indigo-950 border border-indigo-700 rounded-full text-indigo-300 text-xs font-medium mb-2">
          Final Year Project · Computer Engineering
        </div>
        <h1 className="text-5xl md:text-6xl font-bold leading-tight max-w-3xl">
          Detect AI-Generated Voice.{" "}
          <span className="text-indigo-400">Instantly.</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-xl">
          AI voice cloning tools like ElevenLabs can clone any voice from just
          30 seconds of audio — and are actively being used for phone fraud and
          identity impersonation. VoiceVault detects them in real time.
        </p>
        <button
          onClick={() => navigate("/detect")}
          className="mt-4 px-8 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-lg font-semibold transition-all shadow-lg shadow-indigo-900/40"
        >
          Try VoiceVault →
        </button>
      </section>

      {/* Problem stats */}
      <section className="px-6 py-16 bg-gray-900/50">
        <h2 className="text-center text-2xl font-bold mb-10 text-white">
          The Threat is Real
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { stat: "30 seconds", desc: "of audio needed to clone any voice with ElevenLabs" },
            { stat: "Rapidly rising", desc: "AI voice fraud cases reported globally in 2024–25" },
            { stat: "0 tools", desc: "open-source real-time detectors with a usable UI existed before VoiceVault" },
          ].map((item, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 text-center">
              <div className="text-3xl font-bold text-indigo-400 mb-2">{item.stat}</div>
              <div className="text-gray-400 text-sm">{item.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 py-16">
        <h2 className="text-center text-2xl font-bold mb-10">How It Works</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
          {[
            { step: "01", title: "Upload Audio", desc: "Drag and drop any audio file — WAV, MP3, FLAC, M4A, or OGG." },
            { step: "02", title: "RawNet2 Analyzes", desc: "The audio is sliced into 3-second chunks and passed through our trained RawNet2 neural network." },
            { step: "03", title: "Get Verdict", desc: "Receive a Real or Fake verdict with confidence score and a per-chunk timeline heatmap." },
          ].map((item, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-6">
              <div className="text-4xl font-bold text-indigo-900 mb-3">{item.step}</div>
              <div className="text-white font-semibold mb-2">{item.title}</div>
              <div className="text-gray-400 text-sm">{item.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="px-6 py-16 bg-gray-900/50">
        <h2 className="text-center text-2xl font-bold mb-10">Features</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
          {[
            { icon: "🎙", title: "Real-time Detection", desc: "Analyzes uploaded audio instantly, chunk by chunk, with no delays." },
            { icon: "🧠", title: "RawNet2 Neural Network", desc: "22M parameter deep learning model trained on ASVspoof 2019 LA dataset." },
            { icon: "📊", title: "Per-chunk Heatmap", desc: "Visual timeline showing exactly which 3-second segments are real or fake." },
            { icon: "🏆", title: "99.29% AUC", desc: "Evaluated on ASVspoof 2019 LA — detects unseen AI voice attacks." },
          ].map((item, i) => (
            <div key={i} className="bg-gray-900 border border-gray-800 rounded-2xl p-6 flex gap-4">
              <span className="text-3xl">{item.icon}</span>
              <div>
                <div className="text-white font-semibold mb-1">{item.title}</div>
                <div className="text-gray-400 text-sm">{item.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Tech stack */}
      <section className="px-6 py-12">
        <h2 className="text-center text-2xl font-bold mb-8">Built With</h2>
        <div className="flex flex-wrap justify-center gap-3 max-w-2xl mx-auto">
          {["React", "FastAPI", "PyTorch", "RawNet2", "librosa", "ASVspoof 2019", "Tailwind CSS", "wavesurfer.js"].map((tech) => (
            <span key={tech} className="px-4 py-2 bg-gray-900 border border-gray-700 rounded-full text-sm text-gray-300">
              {tech}
            </span>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16 text-center">
        <h2 className="text-3xl font-bold mb-4">Ready to detect a fake voice?</h2>
        <p className="text-gray-400 mb-8">Upload any audio file and get a verdict in seconds.</p>
        <button
          onClick={() => navigate("/detect")}
          className="px-8 py-4 bg-indigo-600 hover:bg-indigo-500 rounded-xl text-lg font-semibold transition-all"
        >
          Try VoiceVault →
        </button>
      </section>

    </div>
  );
}