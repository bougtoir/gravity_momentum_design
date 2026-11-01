"""Generate publication figures (Phase 10) into results/figures/."""
import os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAB = os.path.join(ROOT, "results", "tables")
FIG = os.path.join(ROOT, "results", "figures")
os.makedirs(FIG, exist_ok=True)

plt.rcParams.update({"font.size": 9, "figure.dpi": 300, "savefig.dpi": 300,
                     "font.family": "DejaVu Sans", "axes.linewidth": 0.8})

GLINES = [(1.0, "Earth"), (0.38, "Mars"), (0.165, "Moon")]
VCOL = dict(hinged="#1f77b4", lateral_slide="#ff7f0e", vertical_guided="#2ca02c",
            neg_control="#7f7f7f", chair="#1f77b4", linear="#ff7f0e",
            straddle="#2ca02c", rotary="#9467bd", lateral_lever="#1f77b4",
            axial_lever="#2ca02c", push_pull="#ff7f0e", flat="#1f77b4",
            centering="#ff7f0e", guided="#2ca02c", conventional="#1f77b4",
            guided_rail="#ff7f0e", captive="#2ca02c")


def annotate_g(ax):
    for g, lab in GLINES:
        ax.axvline(g, ls=":", lw=0.8, c="0.4")
        ax.text(g, ax.get_ylim()[1] * 0.97, lab, rotation=0, fontsize=7,
                ha="center", va="top", color="0.3")


def fig1_concept():
    fig, ax = plt.subplots(figsize=(6.5, 4.0))
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)

    def box(x, y, w, h, title, body, fc):
        ax.add_patch(FancyBboxPatch((x, y), w, h,
                                    boxstyle="round,pad=0.012", fc=fc,
                                    ec="0.35", lw=0.9))
        ax.text(x + w / 2, y + h - 0.055, title, ha="center", va="center",
                fontsize=8.6, fontweight="bold")
        ax.text(x + w / 2, y + (h - 0.10) / 2, body, ha="center",
                va="center", fontsize=7.8)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                    xycoords="axes fraction", textcoords="axes fraction",
                    arrowprops=dict(arrowstyle="-|>", lw=1.3, color="0.25"))

    # Earth regime
    box(0.16, 0.78, 0.68, 0.20,
        "Earth regime ($g = g_{\\rm Earth}$)",
        "gravity $g$  →  normal force $N \\approx m g$  →  "
        "friction capacity $\\mu f_u N$\n"
        "→ passive stabilization supplied 'for free'",
        "#e8f0e8")

    arrow(0.50, 0.78, 0.50, 0.64)
    ax.text(0.53, 0.705,
            "$g^* = g / g_{\\rm Earth}$ falls (Moon 0.165, Mars 0.38)",
            fontsize=7.6, transform=ax.transAxes, color="0.25")

    # Partial gravity
    box(0.16, 0.44, 0.68, 0.20,
        "Partial gravity ($0.05 \\leq g^* \\leq 1.0$)",
        "inertial mass $m$ and yaw inertia $I$ unchanged,\n"
        "but friction and torque capacity scale $\\propto g$",
        "#fdf3e0")

    arrow(0.34, 0.44, 0.26, 0.30)
    arrow(0.66, 0.44, 0.74, 0.30)

    box(0.02, 0.04, 0.46, 0.26,
        "Conventional interface",
        "transverse/angular demand\n"
        "exceeds capacity → impulse\n"
        "(UTI, UAI) → correction",
        "#fbe4e4")
    box(0.52, 0.04, 0.46, 0.26,
        "Momentum-aware interface",
        "geometry reduces demand\n"
        "at the source → momentum\n"
        "never generated",
        "#e2f0e2")

    fig.savefig(os.path.join(FIG, "fig1_concept.png"), bbox_inches="tight")
    plt.close(fig)


def fig2_framework():
    fig, ax = plt.subplots(figsize=(6.0, 3.6))
    ax.axis("off")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.plot([0.2], [0.15], "o", ms=10, color="k")
    ax.text(0.20, 0.08, "occupant COM", fontsize=8, ha="center")
    ax.arrow(0.2, 0.15, 0.45, 0.30, head_width=0.02, color="k", lw=1.2)
    ax.text(0.62, 0.50, "reaction $R$", fontsize=9)
    ax.arrow(0.2, 0.15, 0.45, 0.10, head_width=0.02, color="#2ca02c", lw=1.2)
    ax.text(0.58, 0.28, "$F_{\\parallel}$ (task-relevant, $e_d$)", fontsize=8,
            color="#2ca02c")
    ax.arrow(0.65, 0.25, 0.0, 0.20, head_width=0.02, color="#d62728", lw=1.2)
    ax.text(0.67, 0.34, "$F_{\\perp}$ (task-irrelevant)", fontsize=8,
            color="#d62728")
    ax.plot([0.05, 0.35], [0.13, 0.13], color="0.4", lw=3)
    ax.text(0.38, 0.02,
            "support surface:\ncapacity $\\mu f_u N = \\mu f_u m g\\;(+R_v)$",
            fontsize=8, color="0.3")
    ax.text(0.05, 0.85,
            "$\\mathrm{UTI} = \\int \\max(|F_{\\perp}|(1-\\eta_g) - "
            "F_{\\mathrm{cap}}, 0)\,dt$\n"
            "$\\mathrm{UAI} = \\int \\max(|\\tau|(1-\\eta_\\tau) - "
            "\\tau_{\\mathrm{cap}}, 0)\,dt$\n"
            "$\\Gamma_T = \\max|F_{\\perp}| / (\\mu f_u m g)$",
            fontsize=9)
    fig.savefig(os.path.join(FIG, "fig2_framework.png"), bbox_inches="tight")
    plt.close(fig)


def fig3_response(sweep):
    fig, axes = plt.subplots(1, 3, figsize=(7.5, 2.6), sharex=True)
    d = sweep[sweep.case == "door"]
    for v in ["hinged", "lateral_slide", "vertical_guided", "neg_control"]:
        dd = d[d.variant == v]
        axes[0].plot(dd.g_star, dd.UTI, color=VCOL[v],
                     ls="--" if v == "neg_control" else "-",
                     label=v.replace("_", " "))
        axes[1].plot(dd.g_star, dd.UAI, color=VCOL[v],
                     ls="--" if v == "neg_control" else "-")
        axes[2].plot(dd.g_star, dd.gamma_T, color=VCOL[v],
                     ls="--" if v == "neg_control" else "-")
    axes[0].set_ylabel("UTI [N·s]"); axes[1].set_ylabel("UAI [N·m·s]")
    axes[2].set_ylabel("$\\Gamma_T$ [–]")
    for ax in axes:
        ax.set_xlabel("$g^* = g/g_{\\rm Earth}$")
        annotate_g(ax)
    axes[2].axhline(1.0, ls="-", lw=0.7, c="r")
    # (label uses mathtext below)
    axes[0].legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig3_response.png"), bbox_inches="tight")
    plt.close(fig)


def fig4_designs():
    """Five canonical classes: conventional variant(s) on the left of each
    panel, momentum-aware candidate(s) on the right."""
    fig, axes = plt.subplots(1, 5, figsize=(8.6, 2.9))
    titles = ["Door / hatch", "Seat ingress", "Control", "Workstation",
              "Circulation"]
    conv = [["hinged"], ["chair turn"], ["rotary", "lateral lever"],
            ["flat"], ["conventional"]]
    aware = [["lateral slide", "vertical guided"],
             ["linear entry", "straddle guided"],
             ["axial lever", "push / pull"],
             ["centering", "guided"],
             ["guided rail", "captive"]]
    for ax, t, cv, aw in zip(axes, titles, conv, aware):
        ax.set_title(t, fontsize=9, pad=6)
        ax.axis("off"); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.text(0.24, 0.955, "conventional", fontsize=6.4, ha="center",
                color="#8c2d2d", style="italic")
        ax.text(0.76, 0.955, "momentum-\naware", fontsize=6.4, ha="center",
                va="top", color="#1e5d1e", style="italic")
        ax.plot([0.5, 0.5], [0.08, 0.90], color="0.8", lw=0.7, ls=":")
        n = max(len(cv), len(aw))
        for i, dv in enumerate(cv):
            y = 0.80 - i * (0.68 / max(n - 1, 1))
            ax.add_patch(FancyBboxPatch((0.03, y - 0.085), 0.42, 0.17,
                                        boxstyle="round,pad=0.012",
                                        fc="#fbe4e4", ec="#8c2d2d", lw=0.8))
            ax.text(0.24, y, dv.replace(" ", "\n") if len(dv) > 14 else dv,
                    ha="center", va="center", fontsize=7.0)
        for i, dv in enumerate(aw):
            y = 0.80 - i * (0.68 / max(n - 1, 1))
            ax.add_patch(FancyBboxPatch((0.55, y - 0.085), 0.42, 0.17,
                                        boxstyle="round,pad=0.012",
                                        fc="#e2f0e2", ec="#1e5d1e", lw=0.8))
            ax.text(0.76, y, dv.replace(" ", "\n") if len(dv) > 14 else dv,
                    ha="center", va="center", fontsize=7.0)
            ax.annotate("", xy=(0.55, y), xytext=(0.45, y),
                        xycoords="axes fraction",
                        arrowprops=dict(arrowstyle="-|>", lw=0.9,
                                        color="0.45"))
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig4_designs.png"), bbox_inches="tight")
    plt.close(fig)


def fig5_synthesis(benefit):
    fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.0), sharex=True)
    markers = dict(door="o", seat="s", control="^", workstation="d",
                   stairs="v")
    for case, grp in benefit.groupby("case"):
        # best variant per case = max mean B_UTI at moon
        best = grp[grp.g_star == grp.g_star.min()]
        v = best.loc[best.B_UTI.idxmax(), "variant"] if len(best) else grp.variant.iloc[0]
        for v in grp.variant.unique():
            dd = grp[grp.variant == v]
            lab = f"{case}:{v.replace('_',' ')}"
            axes[0].plot(dd.g_star, dd.B_UTI.clip(-1, 1), marker=markers[case],
                         ms=2.5, lw=1, label=lab)
            axes[1].plot(dd.g_star, dd.B_UAI.clip(-1, 1), marker=markers[case],
                         ms=2.5, lw=1, label=lab)
    for ax in axes:
        ax.axhline(0, c="0.4", lw=0.7)
        ax.set_xlabel("$g^* = g/g_{\\rm Earth}$")
        annotate_g(ax)
        ax.invert_xaxis()
    axes[0].set_ylabel(
        "$B_{UTI} = 1 - UTI_{red}/UTI_{conv}$")
    axes[1].set_ylabel(
        "$B_{UAI} = 1 - UAI_{red}/UAI_{conv}$")
    axes[1].legend(fontsize=5.2, frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig5_synthesis.png"), bbox_inches="tight")
    plt.close(fig)


def fig6_regime(sweep):
    fig, ax = plt.subplots(figsize=(6.5, 3.2))
    d = sweep[sweep.case == "door"]
    base = d[d.variant == "hinged"]
    ax.plot(base.g_star, base.gamma_T, color="#1f77b4", lw=1.5,
            label="hinged door $\\Gamma_T$")
    ax.plot(d[d.variant == "vertical_guided"].g_star,
            d[d.variant == "vertical_guided"].gamma_T, color="#2ca02c",
            lw=1.5, label="vertical-guided $\\Gamma_T$")
    ax.axhline(1.0, ls="--", c="r", lw=1)
    ax.text(0.07, 1.05, "$\\Gamma_T = 1$: friction demand bound", fontsize=7.5,
            color="r")
    ax.axvspan(0.05, 0.25, color="#fdd", alpha=0.4)
    ax.axvspan(0.25, 0.6, color="#ffe9c7", alpha=0.4)
    ax.axvspan(0.6, 1.0, color="#def0db", alpha=0.4)
    ax.text(0.13, ax.get_ylim()[1] * 0.8, "redesign\nbeneficial", fontsize=7.5,
            ha="center")
    ax.text(0.42, ax.get_ylim()[1] * 0.8, "guidance\nbeneficial", fontsize=7.5,
            ha="center")
    ax.text(0.8, ax.get_ylim()[1] * 0.8, "conventional\nadequate", fontsize=7.5,
            ha="center")
    ax.set_xlabel("$g^* = g/g_{\\rm Earth}$")
    ax.set_ylabel("$\\Gamma_T$ [–]")
    ax.legend(fontsize=7, frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "fig6_regime.png"), bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    sweep = pd.read_csv(os.path.join(TAB, "gravity_sweep.csv"))
    benefit = pd.read_csv(os.path.join(TAB, "benefit_curves.csv"))
    fig1_concept(); fig2_framework(); fig3_response(sweep)
    fig4_designs(); fig5_synthesis(benefit); fig6_regime(sweep)
    print("figures written:", sorted(os.listdir(FIG)))
