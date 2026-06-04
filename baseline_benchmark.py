"""
baseline_benchmark.py
Run all 13 classifiers with leak-free SMOTE (in-pipeline) and temporal evaluation.
"""
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, roc_auc_score, log_loss, make_scorer)
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (RandomForestClassifier, ExtraTreesClassifier, 
                                AdaBoostClassifier, GradientBoostingClassifier)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neural_network import MLPClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from catboost import CatBoostClassifier
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings('ignore')

RANDOM_STATE = 42

MODELS = {
    'Logistic Regression': LogisticRegression(max_iter=1000, random_state=RANDOM_STATE),
    'Decision Tree': DecisionTreeClassifier(random_state=RANDOM_STATE),
    'Random Forest': RandomForestClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'Extra Trees': ExtraTreesClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'AdaBoost': AdaBoostClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=RANDOM_STATE),
    'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=RANDOM_STATE),
    'LightGBM': LGBMClassifier(random_state=RANDOM_STATE, verbose=-1),
    'CatBoost': CatBoostClassifier(verbose=0, random_state=RANDOM_STATE),
    'KNN': KNeighborsClassifier(n_neighbors=5),
    'Naive Bayes': GaussianNB(),
    'SVM-RBF': SVC(probability=True, random_state=RANDOM_STATE),
    'MLP': MLPClassifier(hidden_layer_sizes=(100,), max_iter=500, random_state=RANDOM_STATE)
}

SCORING = {
    'accuracy': 'accuracy',
    'precision': make_scorer(precision_score, zero_division=0),
    'recall': make_scorer(recall_score, zero_division=0),
    'f1': make_scorer(f1_score, zero_division=0),
    'roc_auc': 'roc_auc',
    'log_loss': make_scorer(log_loss, greater_is_better=False, needs_proba=True)
}

def benchmark(X_train, y_train, X_test, y_test, dataset_name):
    results = []
    for name, clf in MODELS.items():
        pipe = Pipeline([
            ('smote', SMOTE(random_state=RANDOM_STATE, k_neighbors=5)),
            ('clf', clf)
        ])

        # 10-fold CV
        cv = StratifiedKFold(n_splits=10, shuffle=False)  # temporal: no shuffle
        cv_scores = cross_validate(pipe, X_train, y_train, cv=cv, scoring=SCORING, n_jobs=-1)

        # Hold-out evaluation
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)
        y_prob = pipe.predict_proba(X_test)[:, 1]

        results.append({
            'Model': name,
            'CV_Accuracy': np.mean(cv_scores['test_accuracy']),
            'CV_Std': np.std(cv_scores['test_accuracy']),
            'CV_F1': np.mean(cv_scores['test_f1']),
            'Test_Accuracy': accuracy_score(y_test, y_pred),
            'Test_Precision': precision_score(y_test, y_pred, zero_division=0),
            'Test_Recall': recall_score(y_test, y_pred, zero_division=0),
            'Test_F1': f1_score(y_test, y_pred, zero_division=0),
            'Test_ROC_AUC': roc_auc_score(y_test, y_prob),
            'Test_LogLoss': log_loss(y_test, y_prob)
        })
        print(f"[Done] {name}")

    df = pd.DataFrame(results)
    df.to_csv(f"results/tables/{dataset_name}_baseline.csv", index=False)
    return df

if __name__ == "__main__":
    import os
    os.makedirs("results/tables", exist_ok=True)

    # ToN-IoT
    X_train = pd.read_csv("data/processed/toniot_train.csv").values
    y_train = pd.read_csv("data/processed/toniot_train_labels.csv").values.ravel()
    X_test = pd.read_csv("data/processed/toniot_test.csv").values
    y_test = pd.read_csv("data/processed/toniot_test_labels.csv").values.ravel()
    benchmark(X_train, y_train, X_test, y_test, "toniot")

    # Elliptic
    X_train = pd.read_csv("data/processed/elliptic_train.csv").values
    y_train = pd.read_csv("data/processed/elliptic_train_labels.csv").values.ravel()
    X_test = pd.read_csv("data/processed/elliptic_test.csv").values
    y_test = pd.read_csv("data/processed/elliptic_test_labels.csv").values.ravel()
    benchmark(X_train, y_train, X_test, y_test, "elliptic")
