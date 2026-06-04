"""
calibrate_model.py + bootstrap_ci.py (combined for brevity)
Probability calibration and bootstrap confidence intervals.
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import brier_score_loss, log_loss
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import os

RANDOM_STATE = 42

def calibrate_and_bootstrap(X_train, y_train, X_test, y_test, dataset_name, n_bootstrap=1000):
    # Split train into calibration (10%) and model training (90%)
    X_tr, X_cal, y_tr, y_cal = train_test_split(
        X_train, y_train, test_size=0.1, random_state=RANDOM_STATE, stratify=y_train
    )

    # Base model
    base = XGBClassifier(
        n_estimators=400, max_depth=9, learning_rate=0.04,
        subsample=0.82, colsample_bytree=0.82,
        reg_alpha=0.8, reg_lambda=2.5,
        use_label_encoder=False, eval_metric='logloss', random_state=RANDOM_STATE
    )
    pipe = Pipeline([('smote', SMOTE(random_state=RANDOM_STATE)), ('clf', base)])
    pipe.fit(X_tr, y_tr)

    # Calibrate
    for method in ['sigmoid', 'isotonic']:
        calib = CalibratedClassifierCV(pipe, method=method, cv='prefit')
        calib.fit(X_cal, y_cal)
        prob = calib.predict_proba(X_test)[:, 1]
        brier = brier_score_loss(y_test, prob)
        print(f"[{dataset_name}] {method} Brier: {brier:.4f}")

    # Bootstrap CIs on TEST set
    n_test = len(y_test)
    metrics = {'accuracy': [], 'f1': [], 'mcc': [], 'roc_auc': [], 'brier': []}

    for b in range(n_bootstrap):
        idx = np.random.choice(n_test, size=n_test, replace=True)
        y_b = y_test[idx]
        p_b = prob[idx]
        pred_b = (p_b >= 0.5).astype(int)

        from sklearn.metrics import accuracy_score, f1_score, matthews_corrcoef, roc_auc_score
        metrics['accuracy'].append(accuracy_score(y_b, pred_b))
        metrics['f1'].append(f1_score(y_b, pred_b, zero_division=0))
        metrics['mcc'].append(matthews_corrcoef(y_b, pred_b))
        if len(np.unique(y_b)) > 1:
            metrics['roc_auc'].append(roc_auc_score(y_b, p_b))
        metrics['brier'].append(brier_score_loss(y_b, p_b))

    ci = {k: (np.percentile(v, 2.5), np.percentile(v, 97.5)) for k, v in metrics.items() if v}
    df_ci = pd.DataFrame([{k: f"{np.mean(v):.4f} [{ci[k][0]:.4f}, {ci[k][1]:.4f}]" 
                           for k, v in metrics.items() if v}])
    df_ci.to_csv(f"results/tables/{dataset_name}_bootstrap_ci.csv", index=False)
    print(f"[{dataset_name}] Bootstrap CIs saved.")

if __name__ == "__main__":
    os.makedirs("results/tables", exist_ok=True)
    for ds in ['toniot', 'elliptic']:
        X_train = pd.read_csv(f"data/processed/{ds}_train.csv").values
        y_train = pd.read_csv(f"data/processed/{ds}_train_labels.csv").values.ravel()
        X_test = pd.read_csv(f"data/processed/{ds}_test.csv").values
        y_test = pd.read_csv(f"data/processed/{ds}_test_labels.csv").values.ravel()
        calibrate_and_bootstrap(X_train, y_train, X_test, y_test, ds)
