import matplotlib.pyplot as plt
from matplotlib import ticker
import numpy as np
import pathlib

import cabinetry

from typing import Optional, Union


def norm_factors(
    fit_results: list[cabinetry.fit.FitResults],
    figure_folder: Union[str, pathlib.Path] = "",
    model_names: Optional[list[str]] = None,
) -> None:
    factors = []
    for fit_result in fit_results:
        f = {}
        exclude_set = set(
            [
                label
                for label, t in zip(fit_result.labels, fit_result.types)
                if t != "normfactor"
            ]
        )
        mask = [label not in exclude_set for label in fit_result.labels]

        bestfit = fit_result.bestfit[mask]
        uncertainty = fit_result.uncertainty[mask]
        labels = np.asarray(fit_result.labels)[mask]

        for l, b, u in zip(labels, bestfit, uncertainty):
            f[l] = {"bestfit": b, "uncertainty": u}
        factors.append(f)
    all_labels = sorted(set([l for f in factors for l in f]))

    step_size = 1.0
    num_pars = len(all_labels)
    y_positions = np.arange(num_pars, step=step_size)

    fig, ax = plt.subplots(figsize=(6, 1 + step_size * num_pars / 4), dpi=100)

    colors = ["black", "red", "blue", "green"]
    label_offset = step_size / 4.0
    max_norm = -999999
    min_norm = 999999
    for i_f, f in enumerate(factors):
        bestfit = [
            f[label]["bestfit"] if label in f else np.nan
            for label in all_labels
        ]
        uncertainty = [
            f[label]["uncertainty"] if label in f else np.nan
            for label in all_labels
        ]

        tmp_max = max(
            [b + u for b, u in zip(bestfit, uncertainty)] + [max_norm]
        )
        max_norm = max(max_norm, tmp_max)
        tmp_min = min([b - u for b, u in zip(bestfit, uncertainty)])
        min_norm = min(min_norm, tmp_min)

        ypos = (
            y_positions
            if len(factors) == 1
            else [
                y + label_offset / 2.0 * (len(factors) - 1) - i_f * label_offset
                for y in y_positions
            ]
        )
        ax.errorbar(
            bestfit,
            ypos,
            xerr=uncertainty,
            fmt=".",
            color=colors[i_f % len(colors)],
            label=model_names[i_f] if model_names is not None else None,
        )

    ax.vlines(
        1,
        -step_size / 2.0,
        num_pars - step_size / 2.0,
        linestyles="dotted",
        color="black",
    )

    ax.set_xlim(
        [
            min_norm - 0.15 * (max_norm - min_norm),
            max_norm + 0.75 * (max_norm - min_norm),
        ]
    )
    ax.set_ylim([-step_size / 2.0, num_pars - step_size / 2.0])
    ax.set_yticks(y_positions)
    ax.set_yticklabels(all_labels)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.tick_params(axis="both", which="major", pad=8)
    ax.tick_params(direction="in", top=True, right=True, which="both")
    plt.legend(loc="upper right", frameon=False)

    fig.tight_layout()
    fig.savefig(f"{figure_folder}/normfactors.pdf")
    plt.close(fig)
