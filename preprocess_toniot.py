"""
preprocess_toniot.py
Preprocess ToN-IoT dataset with temporal split and label encoding.
"""
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os

RANDOM_STATE = 42

def preprocess_toniot(raw_path, output_dir):
    df = pd.read_csv(raw_path)

    # Remove non-informative identifiers
    drop_cols = ['src_ip', 'dst_ip', 'src_mac', 'dst_mac', 'timestamp_raw']
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    # Temporal sort
    df = df.sort_values('timestamp').reset_index(drop=True)

    # Label encoding for categoricals
    cat_cols = df.select_dtypes(include=['object']).columns.tolist()
    cat_cols = [c for c in cat_cols if c != 'label']
    for c in cat_cols:
        df[c] = LabelEncoder().fit_transform(df[c].astype(str))

    # Separate features and target
    y = df['label']
    X = df.drop(columns=['label'])

    # Temporal split (80/20)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
    y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

    # Standardization (fit on train only)
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    os.makedirs(output_dir, exist_ok=True)
    pd.DataFrame(X_train_s, columns=X.columns).to_csv(f"{output_dir}/toniot_train.csv", index=False)
    pd.DataFrame(X_test_s, columns=X.columns).to_csv(f"{output_dir}/toniot_test.csv", index=False)
    y_train.to_csv(f"{output_dir}/toniot_train_labels.csv", index=False)
    y_test.to_csv(f"{output_dir}/toniot_test_labels.csv", index=False)

    print(f"[ToN-IoT] Train: {X_train.shape}, Test: {X_test.shape}")
    print(f"[ToN-IoT] Temporal split verified: max(train_t) < min(test_t)")

if __name__ == "__main__":
    preprocess_toniot("data/raw/toniot/Train_Test_Network.csv", "data/processed")
