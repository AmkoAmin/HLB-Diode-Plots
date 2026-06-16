"""Comparison plots (linear + semi-log) for both diodes.

  * SENSE on/off  - effect of 4-wire (Kelvin) sensing on the measured curve
  * temperature   - RT / 60 C / 90 C dependence of the forward characteristic

Output goes to ``figures/sense-comparison/`` and ``figures/temperature/``.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from diode import FIG_DIR, I_OFFSET, load_curve


def _plot(curves, title, subdir, fname, log):
    out = FIG_DIR / subdir
    out.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 5))
    for U, I, label in curves:
        if log:
            ax.semilogy(U, np.abs(I) + I_OFFSET, label=label)
        else:
            ax.plot(U, np.abs(I), label=label)
    ax.set_xlabel("voltage U [V]")
    ax.set_ylabel("|I| + 10 pA [A] (log)" if log else "current |I| [A]")
    ax.set_title(title)
    ax.grid(True, which="both")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out / fname, dpi=300)
    plt.close(fig)


def sense_comparison(diode):
    without = (*load_curve(f"{diode}.Diode-ohneSENS-RT"), "without SENSE")
    with_sense = (*load_curve(f"{diode}.Diode-SENS-RT"), "with SENSE")
    for log in (False, True):
        suffix = "log" if log else "linear"
        _plot([without, with_sense],
              f"Diode {diode} @ RT - 4-wire SENSE on/off ({suffix})",
              "sense-comparison", f"d{diode}_RT_sense_{suffix}.png", log)


def temperature_comparison(diode):
    curves = [
        (*load_curve(f"{diode}.Diode-SENS-RT"), "RT"),
        (*load_curve(f"{diode}.Diode-SENS-60T"), "60 C"),
        (*load_curve(f"{diode}.Diode-SENS-90T"), "90 C"),
    ]
    for log in (False, True):
        suffix = "log" if log else "linear"
        _plot(curves,
              f"Diode {diode} - temperature dependence ({suffix})",
              "temperature", f"d{diode}_temp_{suffix}.png", log)


def main():
    for diode in (1, 2):
        sense_comparison(diode)
        temperature_comparison(diode)
    print(f"comparison plots written to {FIG_DIR}")


if __name__ == "__main__":
    main()
