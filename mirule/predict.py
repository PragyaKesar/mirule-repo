"""Command line back end for the miRULE web pages.

Usage:  python -m mirule.predict <mode> <sequence> [min_len max_len]
Modes:  precursor | mature | primary
Prints one JSON object on stdout. The sequence arrives as a single
argument (never through a shell) and is validated again here.
"""
import json, os, re, sys, tempfile, warnings
from functools import lru_cache
from pathlib import Path
warnings.filterwarnings("ignore")
import numpy as np, joblib, RNA
from .features import (clean_sequence, fold, precursor_features, FEATURES,
                       pair_table, window_features, WINDOW)

ROOT = Path(__file__).resolve().parents[1]
LIMITS = {"precursor": (40, 600), "mature": (60, 600), "primary": (100, 1500)}
MATURE_LEN = 21  # most plant miRNAs are 21 nt


@lru_cache(None)
def load_model(name):
    return joblib.load(ROOT / "models" / name)["model"]


def structure_svg(seq, ss):
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "s.svg")
        RNA.svg_rna_plot(seq, ss, path)
        svg = Path(path).read_text()
    svg = svg[svg.find("<svg"):]
    # ViennaRNA embeds interactive scripts; keep only the drawing.
    return re.sub(r"<script.*?</script>", "", svg, flags=re.S)


def precursor_prob(seq, ss=None, mfe=None, efe=None):
    f = precursor_features(seq, ss, mfe, efe)
    m = load_model("precursor_svm.joblib")
    p = float(m.predict_proba(np.array([[f[c] for c in FEATURES]]))[0, 1])
    return p, f


def run_precursor(seq):
    ss, mfe, efe = fold(seq)
    p, f = precursor_prob(seq, ss, mfe, efe)
    return {"sequence": seq, "length": len(seq), "structure": ss, "mfe": round(mfe, 2),
            "efe": round(efe, 2), "gc": round(f["gc content"], 2),
            "mfei1": round(f["MFE index 1"], 3), "base_pairs": f["no. of base pairs"],
            "hairpins": f["hairpin numbers"], "probability": round(p, 3),
            "is_precursor": p >= 0.5, "svg": structure_svg(seq, ss)}


def run_mature(seq):
    out = run_precursor(seq)
    if not out["is_precursor"]:
        out["candidates"] = []
        return out
    ss = out["structure"]
    starts = list(range(len(seq) - WINDOW + 1))
    pt = pair_table(ss)
    X = np.array([window_features(seq, ss, pt, s) for s in starts])
    prob = load_model("mature_model.joblib").predict_proba(X)[:, 1]
    centre = (ss.rfind("(") + ss.find(")")) / 2
    cands, used = [], []
    for i in np.argsort(-prob):
        s = starts[int(i)]
        if any(abs(s - u) < 10 for u in used):
            continue
        used.append(s)
        end = min(s + MATURE_LEN, len(seq))
        cands.append({"start": s + 1, "end": end, "mature": seq[s:end],
                      "arm": "5p" if s < centre else "3p", "probability": round(float(prob[i]), 3)})
        if len(cands) == 3:
            break
    out["candidates"] = cands
    return out


def run_primary(seq, lo, hi):
    lo, hi = max(60, lo), min(400, hi)
    if hi < lo or hi > len(seq):
        raise ValueError("The primary sequence must be longer than the chosen precursor length.")
    lengths = list(range(lo, hi + 1, 5))
    step = max(3, int(len(seq) * len(lengths) / 300 / 3 + 0.999) * 3)  # keep about 300 windows
    wins = []
    for L in lengths:
        for s in range(0, len(seq) - L + 1, step):
            sub = seq[s:s + L]
            p, f = precursor_prob(sub)
            wins.append((p, s, L, f["minimum free energy"]))
    wins.sort(reverse=True)
    top = []
    for p, s, L, mfe in wins:
        if any(not (s + L <= t["start"] - 1 or s >= t["end"]) for t in top):
            continue
        top.append({"start": s + 1, "end": s + L, "length": L, "mfe": round(mfe, 2), "probability": round(p, 3)})
        if len(top) == 5:
            break
    best = top[0]
    sub = seq[best["start"] - 1:best["end"]]
    ss, mfe, efe = fold(sub)
    return {"sequence": seq, "length": len(seq), "windows_scanned": len(wins), "step": step,
            "range": [lo, hi], "top": top, "best_sequence": sub, "best_structure": ss,
            "best_svg": structure_svg(sub, ss)}


def main(argv):
    try:
        mode = argv[1]
        if mode not in LIMITS:
            raise ValueError("Unknown analysis.")
        seq = clean_sequence(argv[2] if len(argv) > 2 else "")
        lo, hi = LIMITS[mode]
        if not lo <= len(seq) <= hi:
            raise ValueError(f"Sequence length must be between {lo} and {hi} nt for this analysis.")
        if mode == "precursor":
            res = run_precursor(seq)
        elif mode == "mature":
            res = run_mature(seq)
        else:
            res = run_primary(seq, int(argv[3]), int(argv[4]))
        res["ok"] = True
    except (ValueError, IndexError) as e:
        res = {"ok": False, "error": str(e) if str(e) else "Invalid input."}
    print(json.dumps(res))


if __name__ == "__main__":
    main(sys.argv)
