from matplotlib import ticker
from matplotlib import patches
from matplotlib import lines
import matplotlib.pyplot as plt

import numpy as np
import pathlib

import cabinetry

from typing import Optional, Union

from common.logger import logger


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


def pull_plot(
    fit_results: cabinetry.fit.FitResults,
    figure_folder: Union[str, pathlib.Path] = "",
) -> None:
    cabinetry.visualize.pulls(
        fit_results=fit_results, figure_folder=figure_folder
    )


def correlation_matrix(
    fit_results: cabinetry.fit.FitResults,
    figure_folder: Union[str, pathlib.Path] = "",
    pruning_threshold=0.1,
) -> None:
    cabinetry.visualize.correlation_matrix(
        fit_results=fit_results,
        figure_folder=figure_folder,
        pruning_threshold=pruning_threshold,
    )


def ranking(
    ranking_results: cabinetry.fit.RankingResults,
    figure_folder: Union[str, pathlib.Path] = "",
) -> None:
    cabinetry.visualize.ranking(
        ranking_results=ranking_results, figure_folder=figure_folder
    )


def limit_comparison(
    limit_results: list[cabinetry.fit.LimitResults],
    figure_folder: Union[str, pathlib.Path] = "",
    model_names: Optional[list[str]] = None,
) -> None:
    num_results = len(limit_results)
    step_size = 2.0
    y_positions = np.arange(step_size * num_results, step=step_size)
    fig, ax = plt.subplots(
        figsize=(6, 1 + step_size * num_results / 4), dpi=100
    )
    min_limit = 999999
    max_limit = 0

    cl = limit_results[0].confidence_level
    for i, limit_result in enumerate(limit_results):
        max_limit = max(
            [
                max_limit,
                limit_result.expected_limit[4],
                limit_result.observed_limit,
            ]
        )
        min_limit = min(
            [
                min_limit,
                limit_result.expected_limit[0],
                limit_result.observed_limit,
            ]
        )
        two_sigma = patches.Rectangle(
            (limit_result.expected_limit[0], step_size * (i - 0.5)),
            limit_result.expected_limit[4] - limit_result.expected_limit[0],
            step_size,
            facecolor="yellow",
        )
        ax.add_patch(two_sigma)
        one_sigma = patches.Rectangle(
            (limit_result.expected_limit[1], step_size * (i - 0.5)),
            limit_result.expected_limit[3] - limit_result.expected_limit[1],
            step_size,
            facecolor="green",
        )
        ax.add_patch(one_sigma)
        ax.vlines(
            limit_result.observed_limit,
            step_size * (i - 0.5),
            step_size * (i + 0.5),
            color="black",
        )
        ax.vlines(
            limit_result.expected_limit[2],
            step_size * (i - 0.5),
            step_size * (i + 0.5),
            color="black",
            linestyle="dashed",
        )
        if cl != limit_result.confidence_level:
            logger.warning(
                "Limits are obtained for inconsistent confidence levels."
            )

    dummy_observed = lines.Line2D(
        [0],
        [0],
        label="Observed Limit",
        color="black",
        linewidth=1,
        linestyle="solid",
    )
    dummy_expected = lines.Line2D(
        [0],
        [0],
        label="Expected Limit",
        color="black",
        linewidth=1,
        linestyle="dashed",
    )
    dummy_one_sigma = patches.Patch(
        color="green", label=r"Expected $\pm 1\sigma$"
    )
    dummy_two_sigma = patches.Patch(
        color="yellow", label=r"Expected $\pm 2\sigma$"
    )
    handles = [dummy_observed, dummy_expected, dummy_one_sigma, dummy_two_sigma]

    ax.set_xlim(
        [
            min_limit - 0.1 * (max_limit - min_limit),
            max_limit + 0.7 * (max_limit - min_limit),
        ]
    )
    ax.set_xlabel(r"$\mu$")
    ax.set_ylim([-step_size * 0.5, step_size * (num_results - 0.5)])
    ax.set_yticks(y_positions)
    if model_names is not None:
        ax.set_yticklabels(model_names)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.tick_params(axis="both", which="major", pad=8)
    ax.tick_params(direction="in", top=True, right=True, which="both")

    leg = plt.legend(handles=handles, loc="upper right", frameon=False)
    leg.set_title(f"All Limits at {int(cl*100)}% CL")

    fig.tight_layout()
    fig.savefig(f"{figure_folder}/limit_comparison.pdf")
    plt.close(fig)
