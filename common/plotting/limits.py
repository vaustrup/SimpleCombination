import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib import lines
from matplotlib import ticker
import numpy as np
import pathlib

import cabinetry

from common.misc.logger import logger


def limit_comparison(
    limit_results: list[cabinetry.fit.LimitResults],
    figure_folder: str | pathlib.Path = "",
    model_names: list[str] | None = None,
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
        observed_limit = limit_result.observed_limit
        expected_limit_two_sigma_down = limit_result.expected_limit[0]
        expected_limit_one_sigma_down = limit_result.expected_limit[1]
        expected_limit = limit_result.expected_limit[2]
        expected_limit_one_sigma_up = limit_result.expected_limit[3]
        expected_limit_two_sigma_up = limit_result.expected_limit[4]
        y_low = step_size * (i - 0.5)
        y_high = step_size * (i + 0.5)

        max_limit = max(
            [
                max_limit,
                expected_limit_two_sigma_up,
                observed_limit,
            ]
        )
        min_limit = min(
            [
                min_limit,
                expected_limit_two_sigma_down,
                observed_limit,
            ]
        )
        two_sigma = patches.Rectangle(
            (expected_limit_two_sigma_down, y_low),
            expected_limit_two_sigma_up - expected_limit_two_sigma_down,
            step_size,
            facecolor="yellow",
        )
        ax.add_patch(two_sigma)
        one_sigma = patches.Rectangle(
            (expected_limit_one_sigma_down, y_low),
            expected_limit_one_sigma_up - expected_limit_one_sigma_down,
            step_size,
            facecolor="green",
        )
        ax.add_patch(one_sigma)
        ax.vlines(
            observed_limit,
            y_low,
            y_high,
            color="black",
        )
        ax.vlines(
            expected_limit,
            y_low,
            y_high,
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
