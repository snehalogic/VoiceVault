
from pathlib import Path
import pandas as pd
from tqdm import tqdm

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

def parse_protocol(split_name: str) -> pd.DataFrame:
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

def verify_files_exist(df: pd.DataFrame) -> int:
    missing = 0
    for path_str in tqdm(df["file_path"], desc="Verifying audio files"):
        if not Path(path_str).exists():
            missing += 1
    return missing

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