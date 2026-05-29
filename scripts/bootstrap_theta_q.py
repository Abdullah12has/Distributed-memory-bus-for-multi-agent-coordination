"""Bootstrap CI on theta_q + predicted-tau* band figure.

Implements Q7 D and ADR-008's "model with uncertainty" framing.

Method:
  1. Load h1_h2_v2/sweep_results.csv (4 compressors × 3 families × 50 workloads
     × 5 seeds × 10 ratios = 30k rows).
  2. Per family, bootstrap-resample workloads (with replacement, n=500
     resamples).
  3. For each resample, re-derive per-family theta_q via the same algorithm
     derive_theta() uses: aggregate over the resampled workloads, find
     first ratio where mean coord_success < success_threshold, record the
     critical_token_recall at that ratio. The MEAN across compressors is
     the bootstrap iterate.
  4. For each (compressor, family) cell, compute predicted_tau using each
     bootstrap iterate's theta_q against the cell's empirical q(r) curve.
     This produces a distribution over predicted tau*.
  5. Empirical tau* per cell is the piecewise-linear fit threshold from
     the existing validation; we read it from theorem_validation_ctr.json.
  6. Report what fraction of cells have empirical_tau within the bootstrap
     band [tau_lo, tau_hi] (95% CI).

Output:
  - results/h1_h2_v2/theorem_validation_bootstrap.json
  - figures/predicted_vs_empirical.{png,pdf} — band overlaid with
    empirical points (3 family panels)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # noqa: E402
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, "src")
from m6.theory.cliff_prediction import predicted_tau


SWEEP_CSV = "results/h1_h2_v2/sweep_results.csv"
EMPIRICAL_TAU_JSON = "results/h1_h2_v2/theorem_validation_ctr.json"
OUT_JSON = "results/h1_h2_v2/theorem_validation_bootstrap.json"
OUT_FIG_PDF = "figures/predicted_vs_empirical.pdf"
OUT_FIG_PNG = "figures/predicted_vs_empirical.png"

N_BOOTSTRAP = 500
SUCCESS_THRESHOLD = 0.5
RECALL_COLUMN = "critical_token_recall"
RNG_SEED = 0


def derive_theta_q_from_subset(df_fam: pd.DataFrame,
                               compressors: list[str],
                               success_threshold: float,
                               recall_column: str) -> float:
    """Re-implementation of derive_theta() restricted to a resampled subset.

    Mean across compressors of the recall at the first ratio where
    coord_success drops below success_threshold.
    """
    per_comp_theta: list[float] = []
    for comp in compressors:
        sub = df_fam[df_fam["compressor"] == comp]
        if sub.empty:
            continue
        agg = (
            sub.groupby("ratio")[["coord_success", recall_column]]
            .mean()
            .reset_index()
            .sort_values("ratio")
        )
        cliff_theta = None
        for _, row in agg.iterrows():
            if row["coord_success"] < success_threshold and row["ratio"] > 1.0:
                cliff_theta = float(row[recall_column])
                break
        if cliff_theta is None and not agg.empty:
            cliff_theta = float(agg.iloc[-1][recall_column])
        if cliff_theta is not None and np.isfinite(cliff_theta):
            per_comp_theta.append(cliff_theta)
    return float(np.mean(per_comp_theta)) if per_comp_theta else float("nan")


def recall_curve_for_cell(df_cell: pd.DataFrame,
                          recall_column: str) -> list[tuple[float, float]]:
    """(ratio, mean_recall) curve for a (compressor, family) cell."""
    agg = (
        df_cell.groupby("ratio")[recall_column]
        .mean()
        .reset_index()
        .sort_values("ratio")
    )
    return [(float(r), float(q)) for r, q in zip(agg["ratio"], agg[recall_column])]


def main() -> None:
    print(f"loading {SWEEP_CSV}…", flush=True)
    df = pd.read_csv(SWEEP_CSV)
    print(f"  {len(df):,} rows, compressors={sorted(df['compressor'].unique())}, "
          f"families={sorted(df['family'].unique())}", flush=True)

    print(f"loading {EMPIRICAL_TAU_JSON}…", flush=True)
    empirical = json.load(open(EMPIRICAL_TAU_JSON))

    families = sorted(df["family"].unique())
    compressors = sorted(df["compressor"].unique())

    rng = np.random.default_rng(RNG_SEED)

    # Per-family bootstrap distribution of theta_q
    theta_q_dist: dict[str, list[float]] = {fam: [] for fam in families}

    # Per-(compressor, family) bootstrap distribution of predicted tau*
    pred_tau_dist: dict[str, dict[str, list[float]]] = {
        comp: {fam: [] for fam in families} for comp in compressors
    }

    # Precompute the per-cell recall curves (used for predicted_tau with each
    # bootstrap theta_q). Recall curves are taken on the FULL data, not the
    # resampled subset — only theta_q is bootstrapped, the q(r) curve is the
    # measurement we trust.
    recall_curves: dict[str, dict[str, list[tuple[float, float]]]] = {}
    for comp in compressors:
        recall_curves[comp] = {}
        for fam in families:
            cell = df[(df["compressor"] == comp) & (df["family"] == fam)]
            recall_curves[comp][fam] = recall_curve_for_cell(cell, RECALL_COLUMN)

    workloads_by_family = {
        fam: sorted(df[df["family"] == fam]["workload_id"].unique())
        for fam in families
    }

    print(f"running {N_BOOTSTRAP} bootstraps…", flush=True)
    for b in range(N_BOOTSTRAP):
        if (b + 1) % 50 == 0:
            print(f"  iteration {b+1}/{N_BOOTSTRAP}", flush=True)
        for fam in families:
            wls = workloads_by_family[fam]
            resampled = rng.choice(wls, size=len(wls), replace=True)
            df_fam = df[(df["family"] == fam) & df["workload_id"].isin(resampled)]
            theta_b = derive_theta_q_from_subset(
                df_fam, compressors, SUCCESS_THRESHOLD, RECALL_COLUMN
            )
            theta_q_dist[fam].append(theta_b)
            if not np.isfinite(theta_b):
                continue
            for comp in compressors:
                pred = predicted_tau(recall_curves[comp][fam], 1, theta_b)
                pred_tau_dist[comp][fam].append(pred)

    # Compute bands and coverage
    theta_q_band: dict[str, dict[str, float]] = {}
    for fam in families:
        arr = np.array([t for t in theta_q_dist[fam] if np.isfinite(t)])
        theta_q_band[fam] = {
            "n_resamples": int(len(arr)),
            "mean": float(np.mean(arr)) if arr.size else float("nan"),
            "median": float(np.median(arr)) if arr.size else float("nan"),
            "ci_lo": float(np.percentile(arr, 2.5)) if arr.size else float("nan"),
            "ci_hi": float(np.percentile(arr, 97.5)) if arr.size else float("nan"),
        }
    print("\nθ_q bootstrap CIs:")
    for fam, band in theta_q_band.items():
        print(f"  family={fam}: mean={band['mean']:.3f} "
              f"CI95=[{band['ci_lo']:.3f}, {band['ci_hi']:.3f}] "
              f"(n={band['n_resamples']})")

    pred_tau_band: dict[str, dict[str, dict[str, float]]] = {}
    cell_coverage = []
    for comp in compressors:
        pred_tau_band[comp] = {}
        for fam in families:
            arr_raw = np.array(pred_tau_dist[comp][fam])
            # Drop inf and NaN; treat inf as "predicted no cliff"
            finite = arr_raw[np.isfinite(arr_raw)]
            n_inf = int((arr_raw == np.inf).sum())
            band = {
                "n_resamples": int(arr_raw.size),
                "n_finite": int(finite.size),
                "n_inf": n_inf,
                "median": float(np.median(finite)) if finite.size else float("nan"),
                "mean": float(np.mean(finite)) if finite.size else float("nan"),
                "ci_lo": float(np.percentile(finite, 2.5)) if finite.size else float("nan"),
                "ci_hi": float(np.percentile(finite, 97.5)) if finite.size else float("nan"),
            }
            empirical_tau = (
                empirical.get(comp, {}).get(fam, {}).get("empirical_tau")
            )
            band["empirical_tau"] = empirical_tau
            if empirical_tau is not None and np.isfinite(empirical_tau) and finite.size:
                in_band = bool(band["ci_lo"] <= empirical_tau <= band["ci_hi"])
                band["empirical_in_band"] = in_band
                cell_coverage.append((comp, fam, in_band))
            else:
                band["empirical_in_band"] = None
            pred_tau_band[comp][fam] = band

    n_total = sum(1 for *_, b in cell_coverage)
    n_in_band = sum(1 for *_, b in cell_coverage if b)
    coverage_rate = n_in_band / max(n_total, 1)

    print(f"\nempirical τ* within bootstrap band: {n_in_band}/{n_total} "
          f"({coverage_rate:.0%})")
    for comp, fam, in_band in cell_coverage:
        marker = "✓" if in_band else "✗"
        b = pred_tau_band[comp][fam]
        emp = b["empirical_tau"]
        print(f"  {marker} {comp:18s} family={fam}: "
              f"emp={emp:.2f}  band=[{b['ci_lo']:.2f}, {b['ci_hi']:.2f}]  "
              f"median={b['median']:.2f}")

    out = {
        "method": (
            "Bootstrap CI on per-family theta_q (workload-level resampling). "
            "Predicted tau* derived from each bootstrap theta_q against the "
            "cell's full-data critical_token_recall curve. Coverage = fraction "
            "of (compressor, family) cells where empirical tau* (from the "
            "piecewise-linear fit in theorem_validation_ctr.json) falls inside "
            "the 95% bootstrap CI on predicted tau*."
        ),
        "n_bootstrap": N_BOOTSTRAP,
        "success_threshold": SUCCESS_THRESHOLD,
        "recall_column": RECALL_COLUMN,
        "rng_seed": RNG_SEED,
        "n_compression_passes": 1,
        "theta_q_band": theta_q_band,
        "predicted_tau_band": pred_tau_band,
        "coverage": {
            "n_total": int(n_total),
            "n_in_band": int(n_in_band),
            "rate": float(coverage_rate),
        },
    }
    Path(OUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nwrote {OUT_JSON}")

    # ------------------------------------------------------------------
    # Figure: 3-panel per-family predicted-τ* band + empirical points
    # ------------------------------------------------------------------
    n_panels = len(families)
    fig, axes = plt.subplots(1, n_panels, figsize=(4.6 * n_panels, 3.8),
                             sharey=False, squeeze=False)
    axes = axes[0]
    palette = {
        "lingua2": "#1f77b4",
        "filter": "#d62728",
        "phi3-extractive": "#2ca02c",
        "truncation": "#9467bd",
    }

    for ai, fam in enumerate(families):
        ax = axes[ai]
        x_positions = []
        for ci, comp in enumerate(compressors):
            b = pred_tau_band[comp][fam]
            color = palette.get(comp, "#444")
            x = ci + 1
            x_positions.append(x)
            # Band as vertical line + caps
            if np.isfinite(b["ci_lo"]) and np.isfinite(b["ci_hi"]):
                ax.plot([x, x], [b["ci_lo"], b["ci_hi"]],
                        color=color, lw=4, alpha=0.45,
                        solid_capstyle="butt")
            if np.isfinite(b["median"]):
                ax.plot(x, b["median"], "_", color=color, markersize=18,
                        markeredgewidth=2.2)
            emp = b["empirical_tau"]
            if emp is not None and np.isfinite(emp):
                in_band = b.get("empirical_in_band")
                marker = "o" if in_band else "x"
                ax.plot(x, emp, marker, color="black", markersize=8,
                        markerfacecolor="white" if in_band else "black",
                        markeredgewidth=1.5)

        ax.set_xticks(x_positions)
        ax.set_xticklabels(compressors, rotation=18, ha="right", fontsize=9)
        ax.set_title(f"Family {fam.upper()}")
        if ai == 0:
            ax.set_ylabel("τ* (compression ratio)")
        ax.set_ylim(0, max(20, 1.05 * max(
            (b["ci_hi"] for b in pred_tau_band["lingua2"].values()
             if np.isfinite(b["ci_hi"])), default=20)))
        ax.grid(alpha=0.25)
        ax.axhline(0, color="black", lw=0.3)

    # Custom legend
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker="o", color="black", linestyle="",
               markerfacecolor="white", markersize=8, markeredgewidth=1.5,
               label="Empirical τ* in band"),
        Line2D([0], [0], marker="x", color="black", linestyle="",
               markersize=8, markeredgewidth=1.5,
               label="Empirical τ* outside band"),
        Line2D([0], [0], color="gray", lw=4, alpha=0.5,
               label="Predicted τ* 95% bootstrap band"),
        Line2D([0], [0], marker="_", color="gray", linestyle="",
               markersize=18, markeredgewidth=2.2,
               label="Predicted τ* median"),
    ]
    fig.legend(handles=legend_elems, loc="lower center", ncol=4,
               bbox_to_anchor=(0.5, -0.03), fontsize=9, frameon=False)
    fig.suptitle(
        f"Predicted τ* (bootstrap 95% CI on θ_q) vs empirical τ*  —  "
        f"{n_in_band}/{n_total} cells within band ({coverage_rate:.0%})",
        fontsize=11, y=0.99,
    )
    fig.tight_layout(rect=(0, 0.06, 1, 0.96))
    Path(OUT_FIG_PDF).parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT_FIG_PDF, bbox_inches="tight")
    fig.savefig(OUT_FIG_PNG, bbox_inches="tight", dpi=160)
    plt.close(fig)
    print(f"wrote {OUT_FIG_PDF} and {OUT_FIG_PNG}")


if __name__ == "__main__":
    main()
