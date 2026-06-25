# VoiceVault — Real-time Deepfake Voice Detection

> Detects AI-generated and voice-cloned audio in real time using RawNet2, a deep neural network trained on the ASVspoof 2019 LA benchmark.

---

## The Problem

AI voice cloning tools like ElevenLabs can clone any voice from just 30 seconds of audio. These synthetic voices are actively being used for phone fraud, identity impersonation, and bypassing voice-based authentication. No open-source, real-time detector with a usable interface existed — until VoiceVault.

---

## How It Works

VoiceVault processes audio in a 5-layer pipeline:

```
Audio Input
    ↓
Preprocessor — resample to 16kHz mono, trim silence, slice into 3s chunks
    ↓
RawNet2 Classifier — raw waveform → sinc filters → residual blocks → GRU → verdict
    ↓
Decision Aggregator — confidence-weighted majority vote across all chunks
    ↓
Output — Real / Fake verdict + confidence score + per-chunk heatmap
```

Each 3-second chunk is analyzed independently. The final verdict is a confidence-weighted combination of all chunk predictions — so a single noisy chunk doesn't throw off the result.

---

## Results

| Model | Features | Dev AUC | Dev Accuracy |
|-------|----------|---------|--------------|
| SVM (baseline) | MFCC mean + std | 0.9017 | 87.22% |
| Random Forest (baseline) | MFCC mean + std | 0.8177 | 91.00% |
| **RawNet2 (final)** | **Raw waveform** | **0.9929** | **97.56%** |

Trained on **ASVspoof 2019 LA** — 25,380 training clips (2,580 real + 22,800 fake across attack types A01–A06). Evaluated on dev split with attack types A01–A06 and generalizes to unseen attacks A07–A19 on the eval split.

---

## Tech Stack

**Frontend**
- React 18 + Vite
- Tailwind CSS
- wavesurfer.js (waveform visualization)
- React Router (landing page + detector routing)

**Backend**
- FastAPI + Uvicorn
- Python 3.13

**ML / Audio Pipeline**
- PyTorch (RawNet2 implementation)
- librosa (audio loading, resampling, silence trimming)
- scikit-learn (baseline SVM and Random Forest)
- NumPy, SciPy

**Dataset**
- ASVspoof 2019 Logical Access (LA) — 121,461 labeled audio clips

**Training**
- Google Colab (NVIDIA Tesla T4 GPU, free tier)

---

## Project Structure

```
VoiceVault/
├── backend/
│   ├── main.py          # FastAPI app — /analyze endpoint
│   ├── inference.py     # Audio loading, chunking, RawNet2 inference
│   ├── model.py         # RawNet2 architecture (SincConv + ResBlocks + GRU)
│   └── rawnet2_best.pt  # Trained model weights (not in repo — see below)
│
├── frontend/
│   └── src/
│       ├── pages/
│       │   ├── Landing.jsx   # Landing page
│       │   └── Detector.jsx  # Main detection UI
│       ├── components/
│       │   ├── Uploader.jsx        # Drag-and-drop audio upload
│       │   ├── Waveform.jsx        # wavesurfer.js waveform display
│       │   ├── Verdict.jsx         # Real/Fake badge + confidence bar
│       │   ├── Heatmap.jsx         # Per-chunk color-coded timeline
│       │   └── ReportDownload.jsx  # Download Report 
│       ├── App.jsx                 # React Router setup
│       └── main.jsx                # Entry point
│
├── build_dataset_index.py    # Parses ASVspoof protocol files → CSV index
├── extract_features.py       # MFCC feature extraction for baseline models
├── train_baseline.py         # Trains SVM + Random Forest baseline
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- ffmpeg ([winget install ffmpeg](https://ffmpeg.org/) on Windows)
- The trained model weights file `rawnet2_best.pt` (see below)

### Model Weights

The trained model file (`rawnet2_best.pt`, 254MB) is not included in this repository due to file size limits. To get it:

**Option A — Train it yourself:**
Follow the Colab training notebook in the `colab/` directory using the ASVspoof 2019 LA dataset from [Kaggle](https://www.kaggle.com/datasets/awsaf49/asvpoof-2019-dataset).

**Option B — Download directly:**
[Google Drive link — (https://drive.google.com/file/d/1PfPn5NZ-dyej-bF6pT8jKp74FRC0fds7/view?usp=sharing)]

Place the file at `backend/rawnet2_best.pt` before starting the backend.

### Backend Setup

```bash
cd backend
pip install fastapi uvicorn python-multipart torch torchaudio librosa soundfile
uvicorn main:app --reload --port 8000
```

The server starts at `http://localhost:8000`. The model loads on startup (~5 seconds). Visit `http://localhost:8000/docs` for the interactive API documentation.

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The app opens at `http://localhost:5173`.

> **Both backend and frontend must be running simultaneously for the app to work.**

---

## API Reference

### `POST /analyze`

Accepts an audio file and returns a deepfake detection verdict.

**Request:** `multipart/form-data` with field `file` (WAV, MP3, FLAC, OGG, M4A — max 50MB)

**Response:**
```json
{
  "verdict": "spoof",
  "confidence": 0.9999,
  "duration": 21.57,
  "num_chunks": 7,
  "chunks": [
    {
      "chunk_idx": 0,
      "start_time": 0.0,
      "end_time": 3.0,
      "label": "spoof",
      "confidence": 1.0,
      "spoof_prob": 1.0
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `verdict` | string | `"bonafide"` (real) or `"spoof"` (fake) |
| `confidence` | float | 0–1, how certain the model is |
| `duration` | float | Audio duration in seconds |
| `num_chunks` | int | Number of 3-second windows analyzed |
| `chunks` | array | Per-chunk breakdown for the heatmap |

---

## Demo

Upload any audio file to detect whether it's a real human voice or AI-generated:

| Test case | Expected verdict |
|-----------|-----------------|
| Your own voice recorded as `.wav` | ✓ Real |
| ElevenLabs generated speech | ✗ Fake |
| WhatsApp voice note (`.ogg`) | May vary — OGG compression artifacts can trigger false positives |

---

## Dataset

**ASVspoof 2019 Logical Access (LA)**
- Train: 2,580 genuine + 22,800 spoofed (attacks A01–A06)
- Dev: 2,548 genuine + 22,296 spoofed (attacks A01–A06)
- Eval: 7,355 genuine + 63,882 spoofed (attacks A07–A19, unseen during training)
- Available at: https://datashare.ed.ac.uk/handle/10283/3336

---

## Architecture — RawNet2

RawNet2 processes raw audio waveforms through:

1. **SincConv** — 128 learnable sinc bandpass filters. Each filter is defined by two learned parameters (low frequency, high frequency), constraining the model to think in frequency bands from the very first layer.
2. **MaxPool + BatchNorm** — downsampling and stabilization
3. **6 Residual Blocks** — progressively deeper feature extraction (128 → 128 → 256 → 256 → 512 → 512 channels)
4. **3-layer GRU** — captures temporal patterns across the 3-second chunk
5. **FC layers** — maps to 2-class output (bonafide / spoof)

Total parameters: **22,184,962**

---

## References

- Tak, H., et al. (2021). *End-to-End anti-spoofing with RawNet2.* ICASSP 2021.
- Wang, X., et al. (2020). *ASVspoof 2019: A large-scale public database of synthesized, converted and replayed speech.* Computer Speech & Language.

---
