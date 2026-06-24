import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";

// Decorative animated waveform
function Waveform() {
  const ref = useRef(null);

  useEffect(() => {
    if (!ref.current) return;
    const patterns = ['','','','active','active','active','fake','fake','real','real','real','active','active','','',''];
    const barCount = 64;
    ref.current.innerHTML = '';
    for (let i = 0; i < barCount; i++) {
      const bar = document.createElement('div');
      bar.className = 'wv-bar';
      const pos = Math.floor((i / barCount) * patterns.length);
      if (patterns[pos]) bar.classList.add(`wv-${patterns[pos]}`);
      bar.style.height = (10 + Math.random() * 36) + 'px';
      bar.style.animationDelay = (Math.random() * 1.4) + 's';
      bar.style.animationDuration = (0.9 + Math.random() * 0.9) + 's';
      ref.current.appendChild(bar);
    }
  }, []);

  return <div ref={ref} className="wv-container" aria-hidden="true" />;
}

export default function Landing() {
  const navigate = useNavigate();

  return (
    <>
      <style>{`
        .wv-container {
          display: flex;
          align-items: center;
          justify-content: center;
          gap: 3px;
          margin: 3.5rem auto 0;
          max-width: 420px;
          height: 60px;
        }
        .wv-bar {
          width: 3px;
          border-radius: 2px;
          background: #1f2937;
          animation: wvwave 1.4s ease-in-out infinite;
        }
        .wv-active { background: #6366f1; }
        .wv-fake   { background: #ef4444; }
        .wv-real   { background: #22c55e; }
        @keyframes wvwave {
          0%, 100% { transform: scaleY(1); }
          50% { transform: scaleY(2.5); }
        }
        .hero-dot {
          width: 6px; height: 6px;
          background: #22c55e;
          border-radius: 50%;
          display: inline-block;
          animation: dotpulse 2s infinite;
        }
        @keyframes dotpulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        .lp-card:hover  { border-color: #374151 !important; transform: translateY(-2px); }
        .lp-feature:hover { border-color: #6366f1 !important; transform: translateY(-2px); }
        .lp-tech:hover  { border-color: #6366f1 !important; color: #a5b4fc !important; }
        .lp-step:hover  { border-color: #374151 !important; transform: translateY(-2px); }
        .lp-nav-btn:hover { opacity: 0.88; transform: translateY(-1px); }
        .lp-outline-btn:hover { border-color: #6366f1 !important; color: #c7d2fe !important; }
      `}</style>

      <div style={{ fontFamily: "'Inter', sans-serif", background: '#030712', color: '#e5e7eb', minHeight: '100vh' }}>

        {/* NAV */}
        <nav style={{
          position: 'sticky', top: 0, zIndex: 100,
          background: 'rgba(3,7,18,0.85)', backdropFilter: 'blur(12px)',
          borderBottom: '1px solid #1f2937', padding: '0 1.5rem'
        }}>
          <div style={{ maxWidth: 1100, margin: '0 auto', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 700, fontSize: '1.15rem', color: '#f9fafb' }}>
              <div style={{ width: 28, height: 28, background: '#6366f1', borderRadius: 7, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                  <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                  <line x1="12" y1="19" x2="12" y2="23"/>
                  <line x1="8" y1="23" x2="16" y2="23"/>
                </svg>
              </div>
              VoiceVault
            </div>
            <button className="lp-nav-btn" onClick={() => navigate('/detect')} style={{
              padding: '0.5rem 1.1rem', borderRadius: 8, fontSize: '0.875rem', fontWeight: 600,
              background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer',
              transition: 'opacity 0.15s, transform 0.15s'
            }}>
              Try it now
            </button>
          </div>
        </nav>

        {/* HERO */}
        <section style={{ padding: '7rem 1.5rem 6rem', textAlign: 'center' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            
            <h1 style={{ fontSize: 'clamp(2.2rem,6vw,4rem)', fontWeight: 900, letterSpacing: '-0.04em', color: '#f9fafb', lineHeight: 1.1, marginBottom: '1.25rem' }}>
              Detect <span style={{ color: '#a5b4fc' }}>AI-Generated</span><br />Voice. Instantly.
            </h1>

            <p style={{ fontSize: 'clamp(0.95rem,2vw,1.1rem)', color: '#9ca3af', maxWidth: 600, margin: '0 auto 2.5rem', lineHeight: 1.7 }}>
              Voice cloning tools like ElevenLabs can replicate anyone's voice from 30 seconds of audio.
              Scammers are already using them — targeting families, bypassing 2FA, committing fraud.
              VoiceVault catches it in real time before the damage is done.
            </p>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              <button className="lp-nav-btn" onClick={() => navigate('/detect')} style={{
                padding: '0.75rem 1.6rem', borderRadius: 10, fontSize: '0.95rem', fontWeight: 600,
                background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer',
                display: 'inline-flex', alignItems: 'center', gap: '0.4rem',
                transition: 'opacity 0.15s, transform 0.15s'
              }}>
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
                Try VoiceVault
              </button>
              <a href="#how-it-works" className="lp-outline-btn" style={{
                padding: '0.75rem 1.6rem', borderRadius: 10, fontSize: '0.95rem', fontWeight: 600,
                background: 'transparent', color: '#a5b4fc', border: '1px solid #374151',
                cursor: 'pointer', textDecoration: 'none', display: 'inline-flex', alignItems: 'center',
                transition: 'border-color 0.15s, color 0.15s'
              }}>
                See how it works
              </a>
            </div>

            <Waveform />
          </div>
        </section>

        <hr style={{ border: 'none', borderTop: '1px solid #111827', margin: 0 }} />

        {/* PROBLEM */}
        <section style={{ padding: '5rem 1.5rem' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <p style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#6366f1', marginBottom: '0.75rem' }}>The threat is real</p>
            <h2 style={{ fontSize: 'clamp(1.6rem,3.5vw,2.4rem)', fontWeight: 800, letterSpacing: '-0.03em', color: '#f9fafb', lineHeight: 1.2, marginBottom: '1rem' }}>
              Voice fraud is scaling faster<br />than defences can keep up.
            </h2>
            <p style={{ color: '#9ca3af', fontSize: '1rem', maxWidth: 560, marginBottom: '3rem' }}>Three facts that make real-time deepfake detection no longer optional.</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(280px,1fr))', gap: '1.25rem' }}>
              {[
                { stat: '30 sec', color: '#ef4444', desc: "That's all the audio a modern voice-cloning model needs to produce an indistinguishable replica — from a YouTube video, a voicemail, or a phone call." },
                { stat: '↑ Rising', color: '#ef4444', desc: 'Voice fraud cases are climbing globally. Attackers impersonate family members, executives, and bank staff — bypassing identity checks with synthesised audio.' },
                { stat: 'Zero', color: '#a5b4fc', desc: 'Open-source, real-time deepfake voice detectors available to everyday developers and end users — until now. Enterprise solutions exist; accessible tooling did not.' },
              ].map((item, i) => (
                <div key={i} className="lp-card" style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 14, padding: '1.75rem', transition: 'border-color 0.2s, transform 0.2s' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, letterSpacing: '-0.04em', color: item.color, marginBottom: '0.3rem' }}>{item.stat}</div>
                  <div style={{ fontSize: '0.85rem', color: '#6b7280', lineHeight: 1.5 }}>{item.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        <hr style={{ border: 'none', borderTop: '1px solid #111827', margin: 0 }} />

        {/* HOW IT WORKS */}
        <section id="how-it-works" style={{ padding: '5rem 1.5rem' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <p style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#6366f1', marginBottom: '0.75rem' }}>How it works</p>
            <h2 style={{ fontSize: 'clamp(1.6rem,3.5vw,2.4rem)', fontWeight: 800, letterSpacing: '-0.03em', color: '#f9fafb', lineHeight: 1.2, marginBottom: '1rem' }}>
              Three steps from audio<br />to verdict.
            </h2>
            <p style={{ color: '#9ca3af', fontSize: '1rem', maxWidth: 560, marginBottom: '3rem' }}>VoiceVault keeps the pipeline transparent so you always know why a clip is flagged.</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: '1.25rem' }}>
              {[
                { num: 'Step 01', title: 'Upload audio', desc: 'Drop any WAV, MP3, FLAC or M4A clip. The frontend sends it to the FastAPI backend ready for inference.' },
                { num: 'Step 02', title: 'RawNet2 analyses in 3-second chunks', desc: 'Each chunk is fed to our PyTorch RawNet2 model trained on ASVspoof 2019. It processes raw waveforms — no hand-crafted features, no spectrograms.' },
                { num: 'Step 03', title: 'Verdict + confidence heatmap', desc: 'You get a per-chunk confidence score and a colour-coded heatmap showing exactly where the model detected synthetic artefacts.', chips: true },
              ].map((item, i) => (
                <div key={i} className="lp-step" style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 14, padding: '1.75rem', transition: 'border-color 0.2s, transform 0.2s' }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, letterSpacing: '0.1em', color: '#6366f1', textTransform: 'uppercase', marginBottom: '0.4rem' }}>{item.num}</div>
                  <div style={{ fontSize: '1rem', fontWeight: 700, color: '#f9fafb', marginBottom: '0.4rem' }}>{item.title}</div>
                  <div style={{ fontSize: '0.85rem', color: '#6b7280', lineHeight: 1.6 }}>{item.desc}</div>
                  {item.chips && (
                    <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                      <span style={{ display:'inline-flex', alignItems:'center', gap:4, padding:'0.25rem 0.65rem', borderRadius:999, fontSize:'0.75rem', fontWeight:700, background:'rgba(34,197,94,0.1)', color:'#22c55e', border:'1px solid rgba(34,197,94,0.2)' }}>● Real</span>
                      <span style={{ display:'inline-flex', alignItems:'center', gap:4, padding:'0.25rem 0.65rem', borderRadius:999, fontSize:'0.75rem', fontWeight:700, background:'rgba(239,68,68,0.1)', color:'#ef4444', border:'1px solid rgba(239,68,68,0.2)' }}>● Fake</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </section>

        <hr style={{ border: 'none', borderTop: '1px solid #111827', margin: 0 }} />

        {/* FEATURES */}
        <section style={{ padding: '5rem 1.5rem' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <p style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.12em', textTransform: 'uppercase', color: '#6366f1', marginBottom: '0.75rem' }}>Features</p>
            <h2 style={{ fontSize: 'clamp(1.6rem,3.5vw,2.4rem)', fontWeight: 800, letterSpacing: '-0.03em', color: '#f9fafb', lineHeight: 1.2, marginBottom: '1rem' }}>
              Built for accuracy,<br />designed for clarity.
            </h2>
            <p style={{ color: '#9ca3af', fontSize: '1rem', maxWidth: 560, marginBottom: '3rem' }}>Everything you need to understand whether a voice is real — with the numbers to back it up.</p>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(240px,1fr))', gap: '1.25rem' }}>
              {[
                { title: 'Real-time Detection', desc: 'Stream audio and receive per-chunk verdicts instantly. No need to wait for the full file to upload before analysis begins.', badge: 'Live inference' },
                { title: 'RawNet2 Neural Network', desc: 'A sinc-filter convolutional architecture that learns directly from raw waveforms, capturing spoofing artefacts invisible to traditional feature extractors.', badge: 'PyTorch' },
                { title: 'Per-chunk Heatmap', desc: 'Every 3-second window is colour-coded green (genuine) or red (synthetic), giving you a visual timeline of exactly where manipulation occurs.', badge: 'Explainable output' },
                { title: '99.29% AUC on ASVspoof 2019', desc: 'Evaluated on the ASVspoof 2019 LA benchmark — the industry-standard dataset for anti-spoofing research — across unseen attack types.', badge: 'Benchmark verified' },
              ].map((item, i) => (
                <div key={i} className="lp-feature" style={{ background: '#111827', border: '1px solid #1f2937', borderRadius: 14, padding: '1.75rem', transition: 'border-color 0.2s, transform 0.2s' }}>
                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f9fafb', marginBottom: '0.35rem' }}>{item.title}</div>
                  <div style={{ fontSize: '0.82rem', color: '#6b7280', lineHeight: 1.6, marginBottom: '0.6rem' }}>{item.desc}</div>
                  <span style={{ display:'inline-block', background:'rgba(34,197,94,0.1)', color:'#22c55e', border:'1px solid rgba(34,197,94,0.2)', borderRadius:999, padding:'0.15rem 0.55rem', fontSize:'0.72rem', fontWeight:700 }}>{item.badge}</span>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* TECH STACK */}
        <section style={{ padding: '3rem 1.5rem', borderTop: '1px solid #1f2937', borderBottom: '1px solid #1f2937' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <div style={{ fontSize: '0.72rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', color: '#4b5563', textAlign: 'center', marginBottom: '1.5rem' }}>Built with</div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
              {[
                { label: 'React', color: '#61dafb' },
                { label: 'FastAPI', color: '#009688' },
                { label: 'PyTorch', color: '#ee4c2c' },
                { label: 'RawNet2', color: '#a5b4fc' },
                { label: 'librosa', color: '#22c55e' },
                { label: 'ASVspoof 2019', color: '#f59e0b' },
              ].map((tech) => (
                <span key={tech.label} className="lp-tech" style={{
                  display: 'inline-flex', alignItems: 'center', gap: '0.45rem',
                  background: '#111827', border: '1px solid #1f2937', borderRadius: 8,
                  padding: '0.45rem 0.85rem', fontSize: '0.82rem', fontWeight: 600,
                  color: '#d1d5db', transition: 'border-color 0.15s, color 0.15s', cursor: 'default'
                }}>
                  <span style={{ width: 7, height: 7, borderRadius: '50%', background: tech.color, flexShrink: 0, display: 'inline-block' }} />
                  {tech.label}
                </span>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section style={{ padding: '5rem 1.5rem', textAlign: 'center' }}>
          <div style={{ maxWidth: 1100, margin: '0 auto' }}>
            <h2 style={{ fontSize: 'clamp(1.6rem,3.5vw,2.4rem)', fontWeight: 800, letterSpacing: '-0.03em', color: '#f9fafb', marginBottom: '1rem' }}>
              Ready to detect a fake voice?
            </h2>
            <p style={{ color: '#9ca3af', marginBottom: '2rem' }}>Upload any audio file and get a verdict in seconds.</p>
            <button className="lp-nav-btn" onClick={() => navigate('/detect')} style={{
              padding: '0.75rem 1.6rem', borderRadius: 10, fontSize: '0.95rem', fontWeight: 600,
              background: '#6366f1', color: '#fff', border: 'none', cursor: 'pointer',
              transition: 'opacity 0.15s, transform 0.15s'
            }}>
              Try VoiceVault →
            </button>
          </div>
        </section>

      </div>
    </>
  );
}