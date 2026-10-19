"""Train the miRULE mature miRNA locator.

The original training table (mature_dataset.csv) could not be reused:
its precursor and mature lists were out of order, so most "mature"
rows encoded the wrong region. This script rebuilds the training set
from the raw plant precursor and mature sequence files.

Precursors are kept when they contain one or two known mature sites
(5p and 3p arms). Precursors with more sites are mostly repeats where
short matures match by chance. A window starting at a known mature 5'
end is a positive example. Windows starting more than 2 nt away from
every known mature are negatives. Features are described in
mirule/features.py (window_features). Evaluation holds out whole
precursors and asks whether the top ranked start is a known start.
"""
import gzip, json, random, sys, time
from pathlib import Path
import numpy as np, joblib, sklearn
from sklearn.ensemble import HistGradientBoostingClassifier

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mirule.features import pair_table, window_features, WINDOW
import RNA

N_TRAIN, N_TEST, N_NEG = 2000, 600, 20
random.seed(7)
read = lambda p: [l.strip().upper().replace("T", "U") for l in gzip.open(p, "rt")]
matures = {m for m in read(ROOT / "data/plant_matures.txt.gz") if 18 <= len(m) <= 24 and set(m) <= set("ACGU")}
precursors = sorted({p for p in read(ROOT / "data/plant_precursors.txt.gz") if 60 <= len(p) <= 400 and set(p) <= set("ACGU")})

by_len = {}
for m in matures:
    by_len.setdefault(len(m), set()).add(m)
pairs = []
for p in precursors:
    starts = set()
    for L, ms in by_len.items():
        for i in range(len(p) - L + 1):
            if p[i:i + L] in ms:
                starts.add(i)
    starts = sorted(s for s in starts if s + WINDOW <= len(p))
    sites = []  # starts within 3 nt (isomiRs) form one site
    for s in starts:
        if sites and s - sites[-1][-1] <= 3:
            sites[-1].append(s)
        else:
            sites.append([s])
    if 1 <= len(sites) <= 2:
        pairs.append((p, starts))
random.shuffle(pairs)
test, train = pairs[:N_TEST], pairs[N_TEST:N_TEST + N_TRAIN]

X, y = [], []
for p, starts in train:
    ss, _ = RNA.fold(p)
    pt = pair_table(ss)
    cand = [s for s in range(len(p) - WINDOW + 1) if all(abs(s - t) > 2 for t in starts)]
    for s in starts:
        X.append(window_features(p, ss, pt, s)); y.append(1)
    for s in random.sample(cand, min(N_NEG, len(cand))):
        X.append(window_features(p, ss, pt, s)); y.append(0)
t0 = time.time()
model = HistGradientBoostingClassifier(max_iter=400, learning_rate=0.05, random_state=0)
model.fit(np.array(X), np.array(y))
fit_s = time.time() - t0

exact = near = 0
for p, starts in test:
    ss, _ = RNA.fold(p)
    pt = pair_table(ss)
    cands = list(range(len(p) - WINDOW + 1))
    prob = model.predict_proba(np.array([window_features(p, ss, pt, s) for s in cands]))[:, 1]
    best = cands[int(np.argmax(prob))]
    exact += best in starts
    near += any(abs(best - t) <= 2 for t in starts)
rand_exact = np.mean([len(st) / (len(p) - WINDOW + 1) for p, st in test])
report = {"precursors_with_1_or_2_mature_sites": len(pairs), "train_precursors": len(train),
          "train_windows": len(y), "train_positive_windows": int(sum(y)),
          "test_precursors": len(test),
          "mean_known_starts_per_test_precursor": float(np.mean([len(s) for _, s in test])),
          "top1_exact_start": exact / len(test), "top1_within_2nt": near / len(test),
          "random_start_baseline_exact": float(rand_exact), "fit_seconds": round(fit_s),
          "scikit_learn": sklearn.__version__}
joblib.dump({"model": model, "window": WINDOW}, ROOT / "models/mature_model.joblib")
(ROOT / "training/mature_report.json").write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
