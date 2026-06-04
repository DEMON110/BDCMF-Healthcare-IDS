"""
preprocess_elliptic.py
Preprocess Elliptic dataset: remove unknown class, temporal split.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
import os

RANDOM_STATE = 42

def preprocess_elliptic(features_path, classes_path, output_dir):
    X = pd.read_csv(features_path)
    y = pd.read_csv(classes_path)

    # Merge
    df = X.merge(y, on='txId')

    # Remove unknown class (class = 2)
    df = df[df['class'] != 2].copy()

    # Binary label: 0 = licit, 1 = illicit
    df['label'] = (df['class'] == 1).astype(int)
    df = df.drop(columns=['txId', 'class'])

    # Temporal split using time step (feature 1)
    df = df.sort_values('1').reset_index(drop=True)
    split_idx = int(0.8 * len(df))

    train_df = df.iloc[:split_idx]
    test_df = df.iloc[split_idx:]

    y_train = train_df['label']
    y_test = test_df['label']
    X_train = train_df.drop(columns=['label'])
    X_test = test_df.drop(columns=['label'])

    # Remove zero-variance features
    zero_var = X_train.columns[X_train.var() == 0]
    X_train = X_train.drop(columns=zero_var)
    X_test = X_test.drop(columns=zero_var)

    # Standardize
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame(X_train_s, columns=X_train.columns).to_csv(f"{output_dir}/elliptic_train.csv", index=False)
    pd.DataFrame(X_test_s, columns=X_test.columns).to_csv(f"{output_dir}/elliptic_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/elliptic_train_labels.csv", index=False)
    y_test.to_csv(f"{output_dir}/elliptic_test_labels.csv", index=False)

    print(f"[Elliptic] Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"[Elliptic] Illicit ratio: train={y_train.mean():.4f}, test={y_test.mean():.4f}")

if __name__ == "__main__":
    preprocess_elliptic(
        "data/raw/elliptic/elliptic_txs_features.csv",
        "data/raw/elliptic/elliptic_txs_classes.csv",
        "data/processed"
    )
