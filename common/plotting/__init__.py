import pathlib

import cabinetry

from typing import Optional, Union

import common.plotting.normalisation
import common.plotting.limits


def norm_factors(
    fit_results: list[cabinetry.fit.FitResults],
    figure_folder: Union[str, pathlib.Path] = "",
    model_names: Optional[list[str]] = None,
) -> None:
    common.plotting.normalisation.norm_factors(
        fit_results=fit_results,
        figure_folder=figure_folder,
        model_names=model_names,
    )


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
    common.plotting.limits.limit_comparison(
        limit_results=limit_results,
        figure_folder=figure_folder,
        model_names=model_names,
    )
