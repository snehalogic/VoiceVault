from pathlib import Path
import base64
import io

import numpy as np
import torch
import torch.nn.functional as F
import librosa
import librosa.display
import matplotlib
matplotlib.use("Agg")         
import matplotlib.pyplot as plt
import matplotlib.cm as cm

from model import RawNet2

SAMPLE_RATE   = 16000
CHUNK_SECONDS = 3.0
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_SECONDS)   # 48 000
DEVICE        = torch.device("cpu")
MODEL_PATH    = Path(__file__).parent / "rawnet2_best.pt"

def load_model() -> RawNet2:
    model = RawNet2(num_classes=2)
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    print(f"RawNet2 loaded from {MODEL_PATH}")
    print(f"Checkpoint epoch : {checkpoint.get('epoch', '?')}  "
          f"Best AUC: {checkpoint.get('best_auc', '?'):.4f}")
    return model

def load_and_chunk(audio_path: str) -> tuple[list[np.ndarray], float]:
    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    audio, _ = librosa.effects.trim(audio, top_db=30)
    duration  = len(audio) / SAMPLE_RATE

    if len(audio) <= CHUNK_SAMPLES:
        return [np.pad(audio, (0, CHUNK_SAMPLES - len(audio)))], duration

    chunks = []
    num_full = len(audio) // CHUNK_SAMPLES
    for i in range(num_full):
        chunks.append(audio[i * CHUNK_SAMPLES : (i + 1) * CHUNK_SAMPLES])

    remainder = audio[num_full * CHUNK_SAMPLES:]
    if len(remainder) >= 0.3 * CHUNK_SAMPLES:
        chunks.append(np.pad(remainder, (0, CHUNK_SAMPLES - len(remainder))))

    return chunks, duration

class GradCAM2D:

    def __init__(self, model: RawNet2):
        self.model = model

        self._sinc_act:  torch.Tensor | None = None   # (B, 128, T_sinc)
        self._sinc_grad: torch.Tensor | None = None
        self._res_act:   torch.Tensor | None = None   # (B, 512, T_res)
        self._res_grad:  torch.Tensor | None = None

        self._fwd_sinc = model.sinc_conv.register_forward_hook(self._save_sinc_act)
        self._bwd_sinc = model.sinc_conv.register_full_backward_hook(self._save_sinc_grad)

        self._fwd_res  = model.res_blocks[-1].conv2.register_forward_hook(self._save_res_act)
        self._bwd_res  = model.res_blocks[-1].conv2.register_full_backward_hook(self._save_res_grad)

    def _save_sinc_act(self, m, inp, out):
        self._sinc_act  = out.detach()

    def _save_sinc_grad(self, m, gin, gout):
        self._sinc_grad = gout[0].detach()

    def _save_res_act(self, m, inp, out):
        self._res_act  = out.detach()

    def _save_res_grad(self, m, gin, gout):
        self._res_grad = gout[0].detach()

    def compute(
        self,
        waveform:     torch.Tensor,   # (1, 1, N)
        target_class: int,            # 0 = bonafide, 1 = spoof
        n_mels:       int = 128,
        n_frames:     int = 188,      # mel-spectrogram time axis for 3s @ hop=256
    ) -> np.ndarray:

        self.model.zero_grad()
        waveform = waveform.requires_grad_(True)
        logits   = self.model(waveform)        # (1, 2)

        score = logits[0, target_class]
        score.backward()

        sinc_grad = self._sinc_grad            # (1, 128, T_sinc)
        sinc_act  = self._sinc_act             # (1, 128, T_sinc)

        freq_weights = sinc_grad.mean(dim=2).squeeze(0)    # (128,)
        freq_act_avg = sinc_act.mean(dim=2).squeeze(0)     # (128,)  mean activation per band

        freq_profile = F.relu(freq_weights * freq_act_avg) # (128,)
        freq_profile = freq_profile.cpu().numpy()

        if freq_profile.max() > 0:
            freq_profile = freq_profile / freq_profile.max()

        res_grad = self._res_grad              # (1, 512, T_res)
        res_act  = self._res_act               # (1, 512, T_res)

        time_weights = res_grad.mean(dim=2)                        # (1, 512)
        time_cam     = (time_weights.unsqueeze(2) * res_act).sum(dim=1)  # (1, T_res)
        time_profile = F.relu(time_cam).squeeze(0).cpu().numpy()  # (T_res,)

        if time_profile.max() > 0:
            time_profile = time_profile / time_profile.max()

        cam_2d = np.outer(freq_profile, time_profile)   # (128, T_res)

        cam_tensor = torch.tensor(cam_2d, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        cam_up = F.interpolate(
            cam_tensor,
            size=(n_mels, n_frames),
            mode="bilinear",
            align_corners=False,
        ).squeeze().numpy()   # (128, n_frames)


        if cam_up.max() > 0:
            cam_up = cam_up / cam_up.max()

        return cam_up   # (128, n_frames)  in [0, 1]

    def remove_hooks(self):
        self._fwd_sinc.remove()
        self._bwd_sinc.remove()
        self._fwd_res.remove()
        self._bwd_res.remove()

def build_gradcam_image(
    chunk:     np.ndarray,   # raw waveform  (48000,)
    cam_2d:    np.ndarray,   # grad-cam      (128, T_frames)  in [0,1]
    label:     str,          # "spoof" or "bonafide"
    chunk_idx: int,
) -> str:

    N_MELS    = 128
    HOP       = 256
    N_FFT     = 1024

    S    = librosa.feature.melspectrogram(
        y=chunk, sr=SAMPLE_RATE,
        n_mels=N_MELS, fmax=8000,
        n_fft=N_FFT, hop_length=HOP,
    )
    S_db = librosa.power_to_db(S, ref=np.max)        # (128, T_frames)
    n_frames = S_db.shape[1]


    if cam_2d.shape != (N_MELS, n_frames):
        cam_t = torch.tensor(cam_2d, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
        cam_2d = F.interpolate(
            cam_t, size=(N_MELS, n_frames), mode="bilinear", align_corners=False
        ).squeeze().numpy()

    freq_profile = cam_2d.mean(axis=1)    # (128,)   — average activation per mel band
    time_profile = cam_2d.mean(axis=0)    # (T_frames,) — average activation per frame

    mel_freqs = librosa.mel_frequencies(n_mels=N_MELS, fmax=8000)  # (128,)

    mel_freqs = librosa.mel_frequencies(n_mels=N_MELS, fmax=8000)  # (128,)

    fig = plt.figure(figsize=(13, 8), facecolor="#0f1117")
    gs  = fig.add_gridspec(
        3, 2,
        height_ratios=[4, 1.3, 0.9],
        width_ratios=[9, 2.5],
        hspace=0.50, wspace=0.30,
    )

    title_color  = "#ff4444" if label == "spoof" else "#44ff88"
    verdict_text = "⚠  FAKE (Spoof)" if label == "spoof" else "✓  REAL (Bonafide)"
    fig.suptitle(
        f"Grad-CAM  —  Chunk {chunk_idx + 1}  |  {verdict_text}",
        color=title_color, fontsize=13, fontweight="bold", y=0.98,
    )

    ax_spec = fig.add_subplot(gs[0, 0])
    ax_spec.set_facecolor("#0f1117")

    librosa.display.specshow(
        S_db,
        sr=SAMPLE_RATE, hop_length=HOP,
        x_axis="time", y_axis="mel",
        fmax=8000, ax=ax_spec,
        cmap="gray",
    )

    extent = [0, CHUNK_SECONDS, 0, 8000]
    im = ax_spec.imshow(
        cam_2d,
        aspect="auto", origin="lower",
        extent=extent,
        cmap="jet",
        alpha=0.50,
        vmin=0.0, vmax=1.0,
    )

    if label == "spoof":
        ax_spec.axhspan(4000, 8000, alpha=0.08, color="#ff0000", linewidth=0)
        ax_spec.annotate(
            "4–8 kHz  vocoder zone",
            xy=(0.02, 6000),           # left edge at x=0.02s
            xycoords="data",
            fontsize=7, color="#ff9999",
            ha="left", va="center",
            bbox=dict(boxstyle="round,pad=0.3", fc="#330000", ec="#ff4444", alpha=0.85),
        )

    ax_spec.set_xlabel("Time (s)", color="#aaaaaa", fontsize=9)
    ax_spec.set_ylabel("Frequency (Hz)", color="#aaaaaa", fontsize=9)
    ax_spec.tick_params(colors="#aaaaaa", labelsize=8)
    for sp in ax_spec.spines.values():
        sp.set_edgecolor("#333333")

    cbar = fig.colorbar(im, ax=ax_spec, pad=0.02, fraction=0.03, aspect=25)
    cbar.set_label("Activation", color="#aaaaaa", fontsize=8)
    cbar.ax.yaxis.set_tick_params(color="#aaaaaa", labelsize=7)
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#aaaaaa")

    ax_freq = fig.add_subplot(gs[0, 1])
    ax_freq.set_facecolor("#0f1117")

    bar_heights = np.diff(mel_freqs, append=mel_freqs[-1] + (mel_freqs[-1] - mel_freqs[-2]))
    ax_freq.barh(
        mel_freqs,
        freq_profile,
        height=bar_heights * 0.9,
        color=plt.cm.jet(freq_profile),
        linewidth=0,
    )


    ax_freq.axhspan(4000, 8000, alpha=0.12, color="#ff4444", linewidth=0)
    ax_freq.text(
        0.95, 6000, "4–8k", color="#ff8888", fontsize=7,
        ha="right", va="center", transform=ax_freq.get_yaxis_transform(),
    )

    ax_freq.set_xlim(0, max(freq_profile.max() * 1.1, 0.05))
    ax_freq.set_ylim(0, 8000)
    ax_freq.set_xlabel("Activation", color="#aaaaaa", fontsize=8)
    ax_freq.set_ylabel("Frequency (Hz)", color="#aaaaaa", fontsize=8)
    ax_freq.tick_params(colors="#aaaaaa", labelsize=7)
    ax_freq.set_title("Frequency\nSaliency", color="#aaaaaa", fontsize=9,
                      fontweight="bold", pad=4)
    for sp in ax_freq.spines.values():
        sp.set_edgecolor("#444444")


    ax_time = fig.add_subplot(gs[1, :])
    ax_time.set_facecolor("#0f1117")

    times = np.linspace(0, CHUNK_SECONDS, n_frames)
    ax_time.fill_between(times, time_profile, alpha=0.65, color="#ff6644")
    ax_time.plot(times, time_profile, color="#ffaa88", linewidth=1.1)
    ax_time.set_xlim(0, CHUNK_SECONDS)
    ax_time.set_ylim(0, max(time_profile.max() * 1.15, 0.05))
    ax_time.set_xlabel("Time (s)", color="#aaaaaa", fontsize=9)
    ax_time.set_ylabel("Activation", color="#aaaaaa", fontsize=8)
    ax_time.set_title(
        "Temporal Saliency  —  which moments drove the decision",
        color="#aaaaaa", fontsize=9, fontweight="bold", pad=4,
    )
    ax_time.tick_params(colors="#aaaaaa", labelsize=8)
    for sp in ax_time.spines.values():
        sp.set_edgecolor("#444444")

    ax_txt = fig.add_subplot(gs[2, :])
    ax_txt.set_facecolor("#0f1117")
    ax_txt.axis("off")

    top5_idx   = np.argsort(freq_profile)[-5:][::-1]
    top5_freqs = mel_freqs[top5_idx]
    top5_vals  = freq_profile[top5_idx]

    summary = "  Most activated bands:   " + "     |     ".join(
        f"{int(f):,} Hz  ({v:.3f})" for f, v in zip(top5_freqs, top5_vals)
    )
    ax_txt.text(
        0.5, 0.5, summary,
        transform=ax_txt.transAxes,
        color="#dddddd", fontsize=8.5,
        va="center", ha="center",
        bbox=dict(
            boxstyle="round,pad=0.5",
            fc="#1a0808" if label == "spoof" else "#081a08",
            ec="#ff4444" if label == "spoof" else "#44ff88",
            alpha=0.9,
        ),
    )


    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")

def predict_chunks(
    model: RawNet2,
    chunks: list[np.ndarray],
    compute_gradcam: bool = True,
) -> list[dict]:

    grad_cam = GradCAM2D(model) if compute_gradcam else None
    results  = []

    model.eval()

    for idx, chunk in enumerate(chunks):
        waveform = torch.tensor(chunk, dtype=torch.float32).unsqueeze(0).unsqueeze(0)

        if compute_gradcam:
            logits = model(waveform)
        else:
            with torch.no_grad():
                logits = model(waveform)

        probs         = F.softmax(logits, dim=1)[0]
        bonafide_prob = probs[0].item()
        spoof_prob    = probs[1].item()
        label         = "spoof" if spoof_prob > bonafide_prob else "bonafide"
        confidence    = max(spoof_prob, bonafide_prob)
        target_class  = 1 if label == "spoof" else 0

        gradcam_b64 = None
        if grad_cam is not None:
            waveform2 = torch.tensor(chunk, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            cam_2d    = grad_cam.compute(waveform2, target_class)   # (128, T_frames)
            gradcam_b64 = build_gradcam_image(chunk, cam_2d, label, idx)

        results.append({
            "chunk_idx":    idx,
            "start_time":   round(idx * CHUNK_SECONDS, 1),
            "end_time":     round((idx + 1) * CHUNK_SECONDS, 1),
            "label":        label,
            "confidence":   round(confidence, 4),
            "spoof_prob":   round(spoof_prob, 4),
            "gradcam_image": gradcam_b64,   # base64 PNG or None
        })
        model.zero_grad()

    if grad_cam is not None:
        grad_cam.remove_hooks()

    return results

def aggregate_verdict(chunk_results: list[dict]) -> tuple[str, float]:
    spoof_weight    = sum(r["spoof_prob"] for r in chunk_results)
    bonafide_weight = sum(1 - r["spoof_prob"] for r in chunk_results)
    total           = spoof_weight + bonafide_weight
    spoof_score     = spoof_weight / total

    if spoof_score >= 0.5:
        return "spoof", round(spoof_score, 4)
    else:
        return "bonafide", round(1 - spoof_score, 4)


def analyze_audio(model: RawNet2, audio_path: str) -> dict:
    chunks, duration = load_and_chunk(audio_path)
    chunk_results    = predict_chunks(model, chunks, compute_gradcam=True)
    verdict, confidence = aggregate_verdict(chunk_results)

    return {
        "verdict":    verdict,
        "confidence": confidence,
        "duration":   round(duration, 2),
        "num_chunks": len(chunks),
        "chunks":     chunk_results,
        "gradcam_image": chunk_results[0]["gradcam_image"] if chunk_results else None,
    }