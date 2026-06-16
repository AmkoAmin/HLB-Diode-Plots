"""Forward voltage U_f from the tangent at U_D = 0.7 V.

A tangent to the linear I-V curve is taken at 0.7 V (central difference); its
x-axis intercept is read off as the forward (threshold) voltage U_f. Plots go
to ``figures/tangents/``.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from diode import FIG_DIR, load_curve

MEASUREMENTS = [
    "1.Diode-SENS-RT", "1.Diode-SENS-60T", "1.Diode-SENS-90T",
    "2.Diode-SENS-RT", "2.Diode-SENS-60T", "2.Diode-SENS-90T",
]
U0, U_MIN, U_MAX = 0.7, 0.4, 0.8


def tangent(U, I, u0=U0):
    sel = (U >= U_MIN) & (U <= U_MAX)
    U, I = U[sel], I[sel]
    i = int(np.argmin(np.abs(U - u0)))
    i = max(1, min(i, len(U) - 2))
    slope = (I[i + 1] - I[i - 1]) / (U[i + 1] - U[i - 1])
    intercept = I[i] - slope * U[i]
    u_f = -intercept / slope if slope else float("nan")
    return slope, intercept, i, u_f, U, I


def save_plot(name):
    out = FIG_DIR / "tangents"
    out.mkdir(parents=True, exist_ok=True)

    U, I = load_curve(name)
    slope, intercept, i, u_f, Us, Is = tangent(U, I)
    line = np.linspace(U_MIN, U_MAX, 200)

    plt.figure(figsize=(7, 5))
    plt.plot(Us, Is, "-", label="measurement")
    plt.plot(line, slope * line + intercept, "--", label="tangent @ 0.7 V")
    plt.scatter([Us[i]], [Is[i]], s=30, zorder=3)
    if U_MIN <= u_f <= U_MAX:
        plt.scatter([u_f], [0], s=30, zorder=3)
        plt.text(u_f, 0, fr"$U_f = {u_f:.3f}$ V", fontsize=9, va="top")
    plt.axhline(0, lw=0.8)
    plt.xlabel("voltage U [V]")
    plt.ylabel("current I [A]")
    plt.title(f"Forward-voltage tangent - {name}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / f"{name}_tangent_0p7V.png", dpi=300)
    plt.close()
    return u_f


def main():
    for name in MEASUREMENTS:
        u_f = save_plot(name)
        print(f"{name:20} U_f = {u_f:.3f} V")
    print(f"\nplots written to {FIG_DIR / 'tangents'}")


if __name__ == "__main__":
    main()
