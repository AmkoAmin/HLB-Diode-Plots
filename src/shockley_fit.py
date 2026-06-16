"""Shockley fit for every measurement.

For each I-V curve this fits the Shockley region, prints the saturation current
``I_S``, the ideality factor ``n`` and the fit quality ``R^2``, and saves a
semi-log plot with the fit window highlighted to ``figures/shockley/``.
"""
import matplotlib
matplotlib.use("Agg")  # file output only, no interactive window
import matplotlib.pyplot as plt
import numpy as np

from diode import (FIG_DIR, I_OFFSET, ideality_factor, load_curve,
                   shockley_fit, temperature_of)

MEASUREMENTS = [
    "1.Diode-SENS-RT", "1.Diode-SENS-60T", "1.Diode-SENS-90T",
    "2.Diode-SENS-RT", "2.Diode-SENS-60T", "2.Diode-SENS-90T",
]


def save_plot(name, U, I, fit, n):
    out = FIG_DIR / "shockley"
    out.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(7, 5))
    plt.semilogy(U, np.abs(I) + I_OFFSET, label="measurement")
    u = np.linspace(fit["u_lo"], fit["u_hi"], 200)
    plt.semilogy(u, np.exp(fit["a"] * u + fit["b"]), "r--", lw=2, label="Shockley fit")
    plt.axvspan(fit["u_lo"], fit["u_hi"], color="yellow", alpha=0.25,
                label=f"fit window [{fit['u_lo']:.2f}, {fit['u_hi']:.2f}] V")
    plt.text(0.05, 0.05, f"$I_S = {fit['I_S']:.2e}$ A\n$n = {n:.2f}$",
             transform=plt.gca().transAxes, fontsize=10,
             bbox=dict(boxstyle="round", fc="white", alpha=0.8))
    plt.xlabel("voltage U [V]")
    plt.ylabel("|I| + 10 pA  [A] (log)")
    plt.title(f"Shockley fit - {name}")
    plt.grid(True, which="both")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out / f"{name}_shockley.png", dpi=300)
    plt.close()


def main():
    print(f"{'measurement':20} {'T [K]':>6} {'I_S [A]':>11} {'n':>6} {'R^2':>8}")
    for name in MEASUREMENTS:
        U, I = load_curve(name)
        fit = shockley_fit(U, I)
        T = temperature_of(name)
        n = ideality_factor(fit["a"], T)
        save_plot(name, U, I, fit, n)
        print(f"{name:20} {T:6.1f} {fit['I_S']:11.2e} {n:6.2f} {fit['r2']:8.4f}")
    print(f"\nplots written to {FIG_DIR / 'shockley'}")


if __name__ == "__main__":
    main()
