"""Check that mirule.features reproduces the stored training features.

data/verification_sequences.tsv lists 200 real precursors whose
sequences were recovered and matched to their rows in the training
table (by length, composition, MFE and base pair count). For each one,
every model feature is recomputed and compared with the stored value.

Run:  python tests/verify_features.py
"""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mirule.features import precursor_features, FEATURES

table = list(csv.DictReader(open(ROOT / "data/precursor_training.csv", encoding="cp1252")))
table = [{k.strip(): v for k, v in r.items()} for r in table]
pairs = list(csv.DictReader(open(ROOT / "data/verification_sequences.tsv"), delimiter="\t"))
ok = {c: 0 for c in FEATURES}
for p in pairs:
    stored = table[int(p["row"])]
    f = precursor_features(p["sequence"])
    for c in FEATURES:
        t = float(stored[c])
        ok[c] += abs(f[c] - t) <= max(1e-4, 1e-5 * abs(t))
worst = min(ok.values()) / len(pairs)
for c in FEATURES:
    print(f"{c:30s} {ok[c]}/{len(pairs)}")
print(f"\nLowest agreement: {worst:.1%}")
sys.exit(0 if worst >= 0.99 else 1)
