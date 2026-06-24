"""
VoiceVault — Day 3: Feature Extraction
-----------------------------------------
Reads dataset_index.csv (built in Day 2), and for every audio file:
  1. Loads it, resampled to 16kHz mono
  2. Trims leading/trailing silence
  3. Slices it into non-overlapping 3-second chunks (padding the last
     chunk with zeros if needed)
  4. Extracts MFCC features per chunk, summarized as mean + std

Outputs three files into D:\VoiceVault\features\:
  - features.npy  : feature matrix, shape (num_chunks, 80)
  - labels.npy    : 0 = bonafide (real), 1 = spoof (fake), shape (num_chunks,)
  - meta.csv      : filename, split, chunk_idx, label  (row-aligned with the above)

Run with:
    python extract_features.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import librosa
from tqdm import tqdm

# -----------------------------------------------------------------------
# 1. CONFIG
# -----------------------------------------------------------------------
INDEX_CSV     = Path(r"D:\VoiceVault\dataset_index.csv")
OUTPUT_DIR    = Path(r"D:\VoiceVault\features")
OUTPUT_DIR.mkdir(exist_ok=True)

SAMPLE_RATE          = 16000   # VoiceVault's standard working sample rate
CHUNK_SECONDS        = 3.0     # core design: every clip becomes 3-second windows
CHUNK_SAMPLES        = int(SAMPLE_RATE * CHUNK_SECONDS)   # = 48000 samples
MIN_REMAINDER_RATIO  = 0.3     # keep trailing partial chunk only if >= 30% full
N_MFCC               = 40      # number of MFCC coefficients per frame

# Only train + dev for now. Add "eval" later when testing on unseen attacks.
SPLITS_TO_PROCESS = ["train", "dev"]

# Label encoding: 0 = real, 1 = fake
LABEL_MAP = {"bonafide": 0, "spoof": 1}


# -----------------------------------------------------------------------
# 2. Load audio and slice into fixed-length chunks
# -----------------------------------------------------------------------
def load_and_chunk(file_path: str) -> list:
    """
    Returns a list of numpy arrays, each exactly CHUNK_SAMPLES long.
    If the clip is shorter than one chunk it is zero-padded to fit.
    """
    audio, _ = librosa.load(file_path, sr=SAMPLE_RATE, mono=True)

    # Trim leading / trailing silence
    audio, _ = librosa.effects.trim(audio, top_db=30)

    # Clip shorter than one full chunk -> pad and return as single chunk
    if len(audio) <= CHUNK_SAMPLES:
        padded = np.pad(audio, (0, CHUNK_SAMPLES - len(audio)))
        return [padded]

    chunks = []
    num_full_chunks = len(audio) // CHUNK_SAMPLES

    for i in range(num_full_chunks):
        start = i * CHUNK_SAMPLES
        chunks.append(audio[start : start + CHUNK_SAMPLES])

    # Leftover tail: keep only if long enough to be meaningful
    remainder = audio[num_full_chunks * CHUNK_SAMPLES :]
    if len(remainder) >= MIN_REMAINDER_RATIO * CHUNK_SAMPLES:
        padded_remainder = np.pad(remainder, (0, CHUNK_SAMPLES - len(remainder)))
        chunks.append(padded_remainder)

    return chunks


# -----------------------------------------------------------------------
# 3. Extract a fixed-length feature vector from one chunk
# -----------------------------------------------------------------------
def extract_features(chunk: np.ndarray) -> np.ndarray:
    """
    Computes 40 MFCCs across the chunk, then takes their mean and std
    over time -> returns a single vector of length 80.

    Why mean + std?
    MFCCs change frame-by-frame, giving a 2D matrix. Taking mean and
    std collapses it to a fixed-size 1D vector that still captures
    both the average spectral shape (mean) and how much it varies (std).
    SVM / Random Forest need this fixed-size vector as input.
    """
    mfcc = librosa.feature.mfcc(y=chunk, sr=SAMPLE_RATE, n_mfcc=N_MFCC)
    mfcc_mean = mfcc.mean(axis=1)   # shape: (40,)
    mfcc_std  = mfcc.std(axis=1)    # shape: (40,)
    return np.concatenate([mfcc_mean, mfcc_std])  # shape: (80,)


# -----------------------------------------------------------------------
# 4. Main
# -----------------------------------------------------------------------
def main():
    index_df = pd.read_csv(INDEX_CSV)
    index_df = index_df[index_df["split"].isin(SPLITS_TO_PROCESS)].reset_index(drop=True)

    print(f"Processing {len(index_df)} files from splits: {SPLITS_TO_PROCESS}")
    print(f"Chunk length: {CHUNK_SECONDS}s  |  Features per chunk: {N_MFCC * 2}\n")

    all_features  = []
    all_labels    = []
    meta_rows     = []
    skipped_files = []

    for _, row in tqdm(index_df.iterrows(), total=len(index_df), desc="Extracting features"):
        try:
            chunks = load_and_chunk(row["file_path"])
        except Exception as e:
            skipped_files.append((row["file_path"], str(e)))
            continue

        label_int = LABEL_MAP[row["label"]]

        for chunk_idx, chunk in enumerate(chunks):
            feature_vector = extract_features(chunk)
            all_features.append(feature_vector)
            all_labels.append(label_int)
            meta_rows.append({
                "filename":  row["filename"],
                "split":     row["split"],
                "chunk_idx": chunk_idx,
                "label":     row["label"],
            })

    X        = np.array(all_features, dtype=np.float32)
    y        = np.array(all_labels,   dtype=np.int64)
    meta_df  = pd.DataFrame(meta_rows)

    np.save(OUTPUT_DIR / "features.npy", X)
    np.save(OUTPUT_DIR / "labels.npy",   y)
    meta_df.to_csv(OUTPUT_DIR / "meta.csv", index=False)

    print(f"\nDone.")
    print(f"Total chunks extracted : {len(X)}")
    print(f"Feature matrix shape   : {X.shape}")
    counts = np.bincount(y)
    print(f"Label distribution     : {counts[0]} bonafide (real), {counts[1]} spoof (fake)")

    if skipped_files:
        print(f"\nWARNING: {len(skipped_files)} files failed to load and were skipped:")
        for path, err in skipped_files[:10]:
            print(f"  {path}: {err}")
        if len(skipped_files) > 10:
            print(f"  ...and {len(skipped_files) - 10} more.")

    print(f"\nSaved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()