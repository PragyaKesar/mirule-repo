"""Train the miRULE precursor classifier (real pre-miRNA vs pseudo hairpin).

Uses the 39 features that miRULE can recompute exactly for any new
sequence (see mirule/features.py). Duplicate rows are removed before
evaluation so that identical sequences never sit in both a training
and a test fold.
"""
import json, sys, warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from pathlib import Path
import numpy as np, pandas as pd, joblib, sklearn
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import accuracy_score, roc_auc_score, matthews_corrcoef, confusion_matrix

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mirule.features import FEATURES

def load(path):
    d = pd.read_csv(path, encoding="cp1252")
    d.columns = [c.strip() for c in d.columns]
    return d

def metrics(y, pred, prob):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"n": int(len(y)), "accuracy": accuracy_score(y, pred),
            "sensitivity": tp / (tp + fn), "specificity": tn / (tn + fp),
            "mcc": matthews_corrcoef(y, pred), "auc": roc_auc_score(y, prob)}

def model():
    return make_pipeline(StandardScaler(), SVC(kernel="rbf", C=1.0, gamma="scale",
                                               probability=True, random_state=0))

raw = load(ROOT / "data/precursor_training.csv")
raw["y"] = (raw["class"].str.strip() == "mirna").astype(int)   # 1 = real pre-miRNA
all87 = [c for c in raw.columns if c not in ("class", "y")]
d = raw.drop_duplicates(subset=all87 + ["y"])
# drop feature vectors that occur with both labels
conflict = d.groupby(FEATURES)["y"].transform("nunique") > 1
d = d[~conflict].drop_duplicates(subset=FEATURES + ["y"]).reset_index(drop=True)
X, y = d[FEATURES].values, d["y"].values
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=10)

report = {"rows_original": int(len(raw)), "rows_after_dedup": int(len(d)),
          "class_counts": {"real": int(y.sum()), "pseudo": int((1 - y).sum())},
          "scikit_learn": sklearn.__version__}

prob = cross_val_predict(model(), X, y, cv=cv, method="predict_proba")[:, 1]
report["cv_39_features"] = metrics(y, (prob >= 0.5).astype(int), prob)

X87 = d[all87].apply(pd.to_numeric, errors="coerce").fillna(0).values
prob87 = cross_val_predict(model(), X87, y, cv=cv, method="predict_proba")[:, 1]
report["cv_87_stored_features"] = metrics(y, (prob87 >= 0.5).astype(int), prob87)

lp = cross_val_predict(make_pipeline(StandardScaler(), LogisticRegression()),
                       d[["length"]].values, y, cv=cv, method="predict_proba")[:, 1]
report["cv_length_only_baseline"] = metrics(y, (lp >= 0.5).astype(int), lp)

final = model().fit(X, y)
t = load(ROOT / "data/independent_testset.csv")
t = t[t["class"].str.strip().isin(["mirna", "pseudo mirna"])]
ty = (t["class"].str.strip() == "mirna").astype(int).values
tp = final.predict_proba(t[FEATURES].values)[:, 1]
report["independent_test_39_features"] = metrics(ty, (tp >= 0.5).astype(int), tp)

joblib.dump({"model": final, "features": FEATURES, "positive": "real pre-miRNA"},
            ROOT / "models/precursor_svm.joblib")
(ROOT / "training/precursor_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
