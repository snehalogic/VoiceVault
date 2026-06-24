"""
VoiceVault — Day 4: Baseline Classifier Training
--------------------------------------------------
Loads the MFCC features extracted in Day 3, trains a Random Forest and
an SVM classifier, evaluates both on the dev split, and saves the best
model to disk.

Why two models?
  - Random Forest: fast to train, no feature scaling needed, gives us a
    quick sanity check that features are actually informative.
  - SVM (RBF kernel): typically stronger on MFCC features, but needs
    StandardScaler first since it's sensitive to feature magnitude.

Both use class_weight='balanced' to handle the 10:1 spoof/bonafide
imbalance in the dataset.

Run with:
    python train_baseline.py
"""

from pathlib import Path
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    roc_auc_score,
    confusion_matrix,
)

# -----------------------------------------------------------------------
# 1. CONFIG
# -----------------------------------------------------------------------
FEATURES_DIR = Path(r"D:\VoiceVault\features")
MODELS_DIR   = Path(r"D:\VoiceVault\models")
MODELS_DIR.mkdir(exist_ok=True)


# -----------------------------------------------------------------------
# 2. Load features
# -----------------------------------------------------------------------
def load_features():
    print("Loading features from disk...")
    X       = np.load(FEATURES_DIR / "features.npy")
    y       = np.load(FEATURES_DIR / "labels.npy")
    meta_df = pd.read_csv(FEATURES_DIR / "meta.csv")

    print(f"  Total chunks loaded : {len(X)}")
    print(f"  Feature vector size : {X.shape[1]}")

    # Split by 'split' column (train vs dev)
    train_mask = meta_df["split"] == "train"
    dev_mask   = meta_df["split"] == "dev"

    X_train, y_train = X[train_mask], y[train_mask]
    X_dev,   y_dev   = X[dev_mask],   y[dev_mask]

    print(f"  Train chunks        : {len(X_train)}"
          f" ({(y_train==0).sum()} real, {(y_train==1).sum()} fake)")
    print(f"  Dev chunks          : {len(X_dev)}"
          f" ({(y_dev==0).sum()} real, {(y_dev==1).sum()} fake)")

    return X_train, y_train, X_dev, y_dev


# -----------------------------------------------------------------------
# 3. Evaluate a trained model and print a clean report
# -----------------------------------------------------------------------
def evaluate(model, X, y, scaler=None, model_name="Model"):
    X_input = scaler.transform(X) if scaler else X
    y_pred  = model.predict(X_input)

    # Probability scores for AUC (use spoof class = column 1)
    if hasattr(model, "predict_proba"):
        y_prob = model.predict_proba(X_input)[:, 1]
    else:
        y_prob = model.decision_function(X_input)

    acc = accuracy_score(y, y_pred)
    auc = roc_auc_score(y, y_prob)
    cm  = confusion_matrix(y, y_pred)

    print(f"\n{'='*55}")
    print(f"  {model_name} — Dev Set Results")
    print(f"{'='*55}")
    print(f"  Accuracy  : {acc*100:.2f}%")
    print(f"  AUC       : {auc:.4f}")
    print(f"\n  Confusion matrix (rows=actual, cols=predicted):")
    print(f"              Pred Real   Pred Fake")
    print(f"  Actual Real   {cm[0][0]:6d}      {cm[0][1]:6d}")
    print(f"  Actual Fake   {cm[1][0]:6d}      {cm[1][1]:6d}")
    print(f"\n  Full classification report:")
    print(classification_report(y, y_pred, target_names=["bonafide", "spoof"]))

    return acc, auc


# -----------------------------------------------------------------------
# 4. Main
# -----------------------------------------------------------------------
def main():
    X_train, y_train, X_dev, y_dev = load_features()

    # --- Scale features (needed for SVM, harmless for RF) ---
    print("\nFitting StandardScaler on train split...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # Save the scaler — inference time must use the same scaling
    joblib.dump(scaler, MODELS_DIR / "scaler.pkl")
    print("  Scaler saved.")

    # ---------------------------------------------------------------
    # Model A: Random Forest (no scaling needed, using raw features)
    # ---------------------------------------------------------------
    print("\nTraining Random Forest...")
    print("  (100 trees, balanced class weights — takes ~1-2 minutes)")
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=None,
        class_weight="balanced",
        n_jobs=-1,          # use all CPU cores
        random_state=42,
    )
    rf.fit(X_train, y_train)
    print("  Done.")

    rf_acc, rf_auc = evaluate(rf, X_dev, y_dev, scaler=None, model_name="Random Forest")
    joblib.dump(rf, MODELS_DIR / "random_forest.pkl")
    print("  Random Forest model saved.")

    # ---------------------------------------------------------------
    # Model B: SVM with RBF kernel (uses scaled features)
    # ---------------------------------------------------------------
    print("\nTraining SVM (RBF kernel)...")
    print("  (This takes longer than RF — roughly 5-15 minutes on 50k chunks)")
    svm = SVC(
        kernel="rbf",
        C=10.0,
        gamma="scale",
        class_weight="balanced",
        probability=True,   # needed for predict_proba / AUC scoring
        random_state=42,
    )
    svm.fit(X_train_scaled, y_train)
    print("  Done.")

    svm_acc, svm_auc = evaluate(svm, X_dev, y_dev, scaler=scaler, model_name="SVM (RBF)")
    joblib.dump(svm, MODELS_DIR / "svm.pkl")
    print("  SVM model saved.")

    # ---------------------------------------------------------------
    # Summary: pick best model
    # ---------------------------------------------------------------
    print(f"\n{'='*55}")
    print("  SUMMARY")
    print(f"{'='*55}")
    print(f"  Random Forest : Accuracy {rf_acc*100:.2f}%  |  AUC {rf_auc:.4f}")
    print(f"  SVM (RBF)     : Accuracy {svm_acc*100:.2f}%  |  AUC {svm_auc:.4f}")

    if svm_auc >= rf_auc:
        best_name = "SVM"
        joblib.dump(svm, MODELS_DIR / "best_baseline.pkl")
        joblib.dump(scaler, MODELS_DIR / "best_baseline_scaler.pkl")
        print(f"\n  Best model    : SVM (AUC {svm_auc:.4f})")
    else:
        best_name = "Random Forest"
        joblib.dump(rf, MODELS_DIR / "best_baseline.pkl")
        print(f"\n  Best model    : Random Forest (AUC {rf_auc:.4f})")

    print(f"  Saved as      : models/best_baseline.pkl")
    print(f"\nWeek 1 target: Accuracy >= 85%, AUC >= 0.90")

    if max(rf_auc, svm_auc) >= 0.90:
        print("  STATUS: TARGET MET — ready to move to Week 2 (RawNet2)")
    else:
        print("  STATUS: Below target — let's debug features before moving on")


if __name__ == "__main__":
    main()