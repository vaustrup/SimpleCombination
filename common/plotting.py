from matplotlib import ticker
import matplotlib.pyplot as plt
import numpy as np
import pathlib

import cabinetry

from typing import Union

def norm_factors(fit_results: cabinetry.fit.FitResults, figure_folder: Union[str, pathlib.Path] = "") -> None:
    exclude_set = set( [label for label, t in zip(fit_results.labels, fit_results.types) if t != "normfactor"] )
    mask = [label not in exclude_set for label in fit_results.labels]

    bestfit = fit_results.bestfit[mask]
    uncertainty = fit_results.uncertainty[mask]
    labels = np.asarray(fit_results.labels)[mask]

    num_pars = len(labels)
    y_positions = np.arange(num_pars)

    fig, ax = plt.subplots(figsize=(6, 1+num_pars/4), dpi=100)

    ax.errorbar(bestfit, y_positions, xerr=uncertainty, fmt="o")

    ax.vlines(1, -0.5, num_pars-0.5, linestyles="dotted", color="black")

    ax.set_xlim([0,3])
    ax.set_ylim([-0.5, num_pars-0.5])
    ax.set_yticks(y_positions)
    ax.set_yticklabels(labels)
    ax.xaxis.set_minor_locator(ticker.AutoMinorLocator())
    ax.tick_params(axis="both", which="major", pad=8)

    fig.tight_layout()
    fig.savefig(f"{figure_folder}/normfactors.pdf")
    plt.close(fig)