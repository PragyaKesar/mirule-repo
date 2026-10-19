"""Feature calculation for miRULE.

Every feature here is computed from the sequence and its RNAfold minimum
free energy structure. Each definition was checked against the values
stored in the original training table (dataset_final.csv). See the
README for the verification results.
"""
import re
import RNA

VALID = re.compile(r"^[ACGU]+$")

DINUC_COLUMNS = {
    "AA": "AA frequency", "AU": "AU frequency", "AG": "AG frequency",
    "AC": "AC frequency", "GA": "GA", "GU": "GU", "GC": "GC", "GG": "GG",
    "CA": "CA", "CU": "CU", "CG": "CG", "CC": "CC", "UA": "UA", "UU": "UU",
    "UG": "UG", "UC": "UC",
}

# Column order used by the deployed precursor model.
FEATURES = [
    "minimum free energy", "length", "no. of base pairs", "no of bp per length",
    "gc content", "free energy per length (dG)", "au content", "GC per length",
    "MFE index 1", "MFE index 4",
    *DINUC_COLUMNS.values(),
    "efe", "mfe-efe", "g/c", "hairpin numbers", "maximum size", "average size",
    "U/A", "A/C", "G %", "U%", "A %", "C %", "gu content",
]


def clean_sequence(raw):
    """Return an uppercase RNA string (FASTA headers removed), or raise ValueError."""
    lines = [l for l in (raw or "").splitlines() if not l.strip().startswith(">")]
    seq = re.sub(r"\s+", "", "".join(lines)).upper().replace("T", "U")
    if not seq:
        raise ValueError("Please enter a sequence.")
    if not VALID.match(seq):
        raise ValueError("The sequence may contain only A, C, G, U (or T).")
    return seq


def fold(seq):
    """RNAfold MFE structure, MFE and ensemble free energy (kcal/mol)."""
    fc = RNA.fold_compound(seq)
    ss, mfe = fc.mfe()
    fc.exp_params_rescale(mfe)
    _, efe = fc.pf()
    return ss, mfe, efe


def hairpin_loops(ss):
    """Sizes of hairpin loops (unpaired run closed by one base pair)."""
    return [len(m.group(1)) for m in re.finditer(r"\((\.*)\)", ss)]


def precursor_features(seq, ss=None, mfe=None, efe=None):
    if ss is None:
        ss, mfe, efe = fold(seq)
    L = len(seq)
    a, c, g, u = (seq.count(n) for n in "ACGU")
    bp = ss.count("(")
    gc = (g + c) / L * 100
    loops = hairpin_loops(ss)
    f = {
        "minimum free energy": mfe,
        "length": L,
        "no. of base pairs": bp,
        "no of bp per length": bp / L,
        "gc content": gc,
        "free energy per length (dG)": mfe / L,
        "au content": (a + u) / L * 100,
        "GC per length": gc / L,
        "MFE index 1": mfe / gc if gc else 0.0,
        "MFE index 4": mfe / bp if bp else 0.0,
        "efe": round(efe, 2),
        "mfe-efe": (mfe - round(efe, 2)) / L,
        "g/c": g / c if c else 0.0,
        "hairpin numbers": len(loops),
        "maximum size": max(loops) if loops else 0,
        "average size": sum(loops) / len(loops) if loops else 0.0,
        "U/A": u / a if a else 0.0,
        "A/C": a / c if c else 0.0,
        "G %": g / L * 100, "U%": u / L * 100,
        "A %": a / L * 100, "C %": c / L * 100,
        "gu content": (g + u) / L * 100,
    }
    # Non-overlapping counts (Python str.count), divided by length,
    # exactly as in the original training table.
    for dn, col in DINUC_COLUMNS.items():
        f[col] = seq.count(dn) / L
    return f


# ---- mature miRNA encoding -------------------------------------------
# Each of 24 positions is coded by nucleotide and pairing state:
# A paired 1, A unpaired 2, C paired 3, C unpaired 4,
# G paired 5, G unpaired 6, U paired 7, U unpaired 8.
CODE = {("A", True): 1, ("A", False): 2, ("C", True): 3, ("C", False): 4,
        ("G", True): 5, ("G", False): 6, ("U", True): 7, ("U", False): 8}
WINDOW = 24


FLANK = 4  # nucleotides upstream of the window included as context


def pair_table(ss):
    """Partner index for each position (-1 if unpaired)."""
    stack, pt = [], [-1] * len(ss)
    for i, c in enumerate(ss):
        if c == "(":
            stack.append(i)
        elif c == ")":
            j = stack.pop()
            pt[i], pt[j] = j, i
    return pt


def window_features(seq, ss, pt, start):
    """Features for a candidate mature 5' start.

    One hot nucleotide and pairing state for 4 nt upstream plus 24 nt
    (code 0 = outside the sequence), followed by position features:
    distances to both ends and to the terminal loop centre, pairing
    within the first 22 nt, and the partner of the first nucleotide.
    """
    L = len(seq)
    codes = [CODE[(seq[i], ss[i] != ".")] if 0 <= i < L else 0
             for i in range(start - FLANK, start + WINDOW)]
    onehot = [0] * (len(codes) * 9)
    for k, c in enumerate(codes):
        onehot[k * 9 + c] = 1
    last_open, first_close = ss.rfind("("), ss.find(")")
    loop = (last_open + first_close) / 2 if 0 <= last_open < first_close else L / 2
    w = ss[start:start + 22]
    p0, p19 = pt[start], pt[min(start + 19, L - 1)]
    extra = [start, L - start, start - loop, abs(start - loop), start + 21 - loop,
             w.count("(") + w.count(")"), int("(" in w and ")" in w),
             p0 - start if p0 >= 0 else -999, p19 if p19 >= 0 else -999, L]
    return onehot + extra
