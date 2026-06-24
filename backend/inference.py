
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F
import librosa

from model import RawNet2

SAMPLE_RATE   = 16000
CHUNK_SECONDS = 3.0
CHUNK_SAMPLES = int(SAMPLE_RATE * CHUNK_SECONDS)   # 48000
DEVICE        = torch.device("cpu")                 # CPU is fine for inference
MODEL_PATH    = Path(__file__).parent / "rawnet2_best.pt"


def load_model() -> RawNet2:
    model = RawNet2(num_classes=2)
    checkpoint = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=False)
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    print(f"RawNet2 loaded from {MODEL_PATH}")
    print(f"Checkpoint epoch: {checkpoint.get('epoch', '?')}  "
          f"Best AUC: {checkpoint.get('best_auc', '?'):.4f}")
    return model

def load_and_chunk(audio_path: str) -> tuple[list[np.ndarray], float]:

    audio, _ = librosa.load(audio_path, sr=SAMPLE_RATE, mono=True)
    audio, _  = librosa.effects.trim(audio, top_db=30)
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

def predict_chunks(model: RawNet2, chunks: list[np.ndarray]) -> list[dict]:
    results = []

    with torch.no_grad():
        for idx, chunk in enumerate(chunks):
            waveform = torch.tensor(chunk, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            # shape: (1, 1, 48000)

            logits = model(waveform)                        # (1, 2)
            probs  = F.softmax(logits, dim=1)[0]           # (2,)

            bonafide_prob = probs[0].item()
            spoof_prob    = probs[1].item()

            label      = "spoof" if spoof_prob > bonafide_prob else "bonafide"
            confidence = max(spoof_prob, bonafide_prob)

            results.append({
                "chunk_idx":   idx,
                "start_time":  round(idx * CHUNK_SECONDS, 1),
                "end_time":    round((idx + 1) * CHUNK_SECONDS, 1),
                "label":       label,
                "confidence":  round(confidence, 4),
                "spoof_prob":  round(spoof_prob, 4),
            })

    return results

def aggregate_verdict(chunk_results: list[dict]) -> tuple[str, float]:
    spoof_weight    = sum(r["spoof_prob"] for r in chunk_results)
    bonafide_weight = sum(1 - r["spoof_prob"] for r in chunk_results)
    total           = spoof_weight + bonafide_weight

    spoof_score = spoof_weight / total

    if spoof_score >= 0.5:
        return "spoof", round(spoof_score, 4)
    else:
        return "bonafide", round(1 - spoof_score, 4)

def analyze_audio(model: RawNet2, audio_path: str) -> dict:

    chunks, duration = load_and_chunk(audio_path)
    chunk_results    = predict_chunks(model, chunks)
    verdict, confidence = aggregate_verdict(chunk_results)

    return {
        "verdict":     verdict,
        "confidence":  confidence,
        "duration":    round(duration, 2),
        "num_chunks":  len(chunks),
        "chunks":      chunk_results,
    }