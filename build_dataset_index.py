"""
VoiceVault — Day 2: Build Dataset Index
-----------------------------------------
Reads the three ASVspoof2019 LA protocol files (train / dev / eval) and
builds one combined CSV that maps every audio file to its full path,
split, and label (bonafide / spoof). Every later script (feature
extraction, training, evaluation) reads from this CSV instead of
touching the raw protocol files again.

Run this once after extracting the dataset:
    python build_dataset_index.py
"""

from pathlib import Path
import pandas as pd
from tqdm import tqdm

# -----------------------------------------------------------------------
# 1. CONFIG — adjust this if your dataset lives somewhere else
# -----------------------------------------------------------------------
BASE_DIR = Path(r"D:\VoiceVault\dataset\LA\LA")

PROTOCOL_DIR = BASE_DIR / "ASVspoof2019_LA_cm_protocols"

PROTOCOLS = {
    "train": PROTOCOL_DIR / "ASVspoof2019.LA.cm.train.trn.txt",
    "dev":   PROTOCOL_DIR / "ASVspoof2019.LA.cm.dev.trl.txt",
    "eval":  PROTOCOL_DIR / "ASVspoof2019.LA.cm.eval.trl.txt",
}

AUDIO_DIRS = {
    "train": BASE_DIR / "ASVspoof2019_LA_train" / "flac",
    "dev":   BASE_DIR / "ASVspoof2019_LA_dev" / "flac",
    "eval":  BASE_DIR / "ASVspoof2019_LA_eval" / "flac",
}

# Where the final combined CSV will be saved
OUTPUT_CSV = Path(r"D:\VoiceVault\dataset_index.csv")


# -----------------------------------------------------------------------
# 2. Parse one protocol file into a DataFrame
# -----------------------------------------------------------------------
def parse_protocol(split_name: str) -> pd.DataFrame:
    """
    Each line in a protocol file looks like:
        LA_0079 LA_T_1138215 - - bonafide
        LA_0079 LA_T_1271820 - A01 spoof

    Columns, in order: speaker_id, filename, unused, system_id, label
    - system_id is '-' for genuine audio, or an attack code (A01-A19) for fake audio
    - label is either "bonafide" (real) or "spoof" (fake)
    """
    protocol_path = PROTOCOLS[split_name]

    df = pd.read_csv(
        protocol_path,
        sep=r"\s+",
        engine="python",
        header=None,
        names=["speaker_id", "filename", "unused", "system_id", "label"],
    )

    df = df.drop(columns=["unused"])
    df["split"] = split_name

    audio_dir = AUDIO_DIRS[split_name]
    df["file_path"] = df["filename"].apply(lambda name: str(audio_dir / f"{name}.flac"))

    return df


# -----------------------------------------------------------------------
# 3. Verify every audio file referenced actually exists on disk
# -----------------------------------------------------------------------
def verify_files_exist(df: pd.DataFrame) -> int:
    missing = 0
    for path_str in tqdm(df["file_path"], desc="Verifying audio files"):
        if not Path(path_str).exists():
            missing += 1
    return missing


# -----------------------------------------------------------------------
# 4. Main
# -----------------------------------------------------------------------
def main():
    print("Reading protocol files...")
    all_splits = []
    for split_name in ["train", "dev", "eval"]:
        df_split = parse_protocol(split_name)
        print(f"  {split_name}: {len(df_split)} rows")
        all_splits.append(df_split)

    full_df = pd.concat(all_splits, ignore_index=True)

    print("\nLabel counts per split:")
    print(full_df.groupby(["split", "label"]).size())

    print("\nVerifying that every referenced audio file actually exists...")
    missing_count = verify_files_exist(full_df)

    if missing_count > 0:
        print(f"\nWARNING: {missing_count} audio files listed in the protocols "
              f"were not found on disk. Check your extraction.")
    else:
        print("\nAll audio files found. Dataset extraction is fully intact.")

    full_df.to_csv(OUTPUT_CSV, index=False)
    print(f"\nSaved combined index to: {OUTPUT_CSV}")
    print(f"Total rows: {len(full_df)}")


if __name__ == "__main__":
    main()