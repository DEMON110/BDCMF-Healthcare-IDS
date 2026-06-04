"""
shap_explain.py
SHAP TreeExplainer, global importance, and ablation study.
"""
import pandas as pd
import numpy as np
import shap
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.pipeline import Pipeline
from sklearn.metrics import f1_score, accuracy_score, roc_auc_score
import matplotlib.pyplot as plt
import os

RANDOM_STATE = 42

def shap_ablation(X_train, y_train, X_test, y_test, feature_names, dataset_name):
    # Train tuned model
    model = XGBClassifier(
        n_estimators=400, max_depth=9, learning_rate=0.04,
        subsample=0.82, colsample_bytree=0.82,
        reg_alpha=0.8, reg_lambda=2.5,
        use_label_encoder=False, eval_metric='logloss', random_state=RANDOM_STATE
    )
    pipe = Pipeline([('smote', SMOTE(random_state=RANDOM_STATE)), ('clf', model)])
    pipe.fit(X_train, y_train)
    clf = pipe.named_steps['clf']

    # SHAP
    explainer = shap.TreeExplainer(clf)
    shap_vals = explainer.shap_values(X_test)
    if isinstance(shap_vals, list):
        shap_vals = shap_vals[1]  # binary: take class 1

    global_imp = np.mean(np.abs(shap_vals), axis=0)
    ranked_idx = np.argsort(global_imp)[::-1]

    # Save top-15 features
    top15 = [(feature_names[i], global_imp[i]) for i in ranked_idx[:15]]
    pd.DataFrame(top15, columns=['Feature', 'Mean|SHAP|']).to_csv(
        f"results/tables/{dataset_name}_shap_top15.csv", index=False)

    # Ablation
    ablation = []
    for k in [5, 10, 15, 20, 25, 30, 35, 40, X_train.shape[1]]:
        sel = ranked_idx[:k]
        X_tr_k = X_train[:, sel]
        X_te_k = X_test[:, sel]
        m = XGBClassifier(random_state=RANDOM_STATE, use_label_encoder=False, eval_metric='logloss')
        m.fit(X_tr_k, y_train)
        p = m.predict(X_te_k)
        ablation.append({
            'Top_k': k,
            'Accuracy': accuracy_score(y_test, p),
            'F1': f1_score(y_test, p, zero_division=0),
            'ROC_AUC': roc_auc_score(y_test, m.predict_proba(X_te_k)[:, 1])
        })

    pd.DataFrame(ablation).to_csv(f"results/tables/{dataset_name}_ablation.csv", index=False)
    print(f"[{dataset_name}] SHAP + Ablation complete.")

if __name__ == "__main__":
    os.makedirs("results/tables", exist_ok=True)
    for ds in ['toniot', 'elliptic']:
        X_train = pd.read_csv(f"data/processed/{ds}_train.csv").values
        y_train = pd.read_csv(f"data/processed/{ds}_train_labels.csv").values.ravel()
        X_test = pd.read_csv(f"data/processed/{ds}_test.csv").values
        y_test = pd.read_csv(f"data/processed/{ds}_test_labels.csv").values.ravel()
        cols = pd.read_csv(f"data/processed/{ds}_train.csv").columns.tolist()
        shap_ablation(X_train, y_train, X_test, y_test, cols, ds)
