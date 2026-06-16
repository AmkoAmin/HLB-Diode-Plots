"""Shared helpers for the diode I-V analysis.

All scripts in ``src/`` build on this module: loading the measured I-V curves,
fitting the Shockley region in the semi-log plot, and deriving the saturation
current ``I_S`` and the ideality factor ``n``.
"""
from pathlib import Path

import numpy as np
import pandas as pd

# Repository layout (this file lives in <repo>/src/)
REPO = Path(__file__).resolve().parent.parent
DATA_DIR = REPO / "data"
FIG_DIR = REPO / "figures"

# Boltzmann constant over elementary charge [V/K]; thermal voltage U_T = KB_Q * T
KB_Q = 8.617333262e-5

# Nominal junction temperatures of the three measurement series
TEMPERATURES_K = {"RT": 300.0, "60T": 333.15, "90T": 363.15}

# Small offset (10 pA) that lifts |I| off zero so it stays plottable on a log axis
I_OFFSET = 10e-12


def load_curve(name):
    """Load one I-V measurement and return ``(U, I)`` as float arrays.

    The source-meter exports a quirky ``"';'"``-quoted CSV with a header line::

        Variable;DC I
        0.0';'3e-05
        0.03';'6e-05
    """
    df = pd.read_csv(DATA_DIR / name, sep="';'", engine="python", skiprows=1, header=None)
    U = df.iloc[:, 0].astype(float).to_numpy()
    I = df.iloc[:, 1].astype(float).to_numpy()
    return U, I


def shockley_fit(U, I, u_min=0.2, u_max=0.9, w_min=8, w_max=25):
    """Fit the most linear ``ln(I)`` vs. ``U`` window (the Shockley region).

    A sliding window over the positive-current samples is scored by R^2; the
    best straight line ``ln(I) = a*U + b`` gives the saturation current
    ``I_S = exp(b)``. Returns a dict with ``a``, ``b``, ``I_S``, the fit window
    ``[u_lo, u_hi]`` and ``r2``.
    """
    mask = (I > 0) & (U >= u_min) & (U <= u_max)
    Uv, Iv = U[mask], I[mask]
    if len(Uv) < w_min + 2:
        raise RuntimeError(f"too few valid points in search range ({len(Uv)})")

    window = min(max(w_min, len(Uv) // 5), w_max)
    best = None
    for start in range(0, len(Uv) - window + 1):
        Uw, Iw = Uv[start:start + window], Iv[start:start + window]
        ln = np.log(Iw)
        a, b = np.polyfit(Uw, ln, 1)
        if a <= 0:  # forward branch must rise
            continue
        ss_res = np.sum((ln - (a * Uw + b)) ** 2)
        ss_tot = np.sum((ln - ln.mean()) ** 2)
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else -np.inf
        if best is None or r2 > best["r2"]:
            best = {"a": float(a), "b": float(b), "I_S": float(np.exp(b)),
                    "u_lo": float(Uw.min()), "u_hi": float(Uw.max()), "r2": float(r2)}
    if best is None:
        raise RuntimeError("no valid Shockley window found")
    return best


def ideality_factor(slope_a, temperature_k):
    """Ideality factor ``n`` from the log-fit slope ``a = q / (n * k * T)``."""
    return 1.0 / (slope_a * KB_Q * temperature_k)


def temperature_of(name):
    """Map a measurement filename (e.g. ``1.Diode-SENS-60T``) to its temperature [K]."""
    return TEMPERATURES_K[name.split("-")[-1]]
