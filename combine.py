import pathlib
import logging
import sys

from common.combinedworkspace import CombinedWorkspace
import common.helpers
import common.plotting
import common.utils

logger = logging.getLogger(__name__)

def main():
    """
    Combine pyhf workspaces and run statistical evaluations.
    """

    args = common.utils.parse_arguments()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)4s]: %(message)s", "%H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(args.output_level)

    parameters = common.utils.parse_parameters(args.parameters)

    combination = common.helpers.get_combination(args.combination_name)
    workspaces = [common.helpers.get_analysis_workspace(analysis_name=analysis_name, parameters=parameters, combination=combination) for analysis_name in args.analysis_names]

    combined_ws = CombinedWorkspace(name="Combined", workspaces=workspaces)
    combined_fit_results = combined_ws.fit_results()
    for label, bestfit, uncertainty in zip(combined_fit_results.labels, combined_fit_results.bestfit, combined_fit_results.uncertainty):
        logger.debug(f"{label}: {bestfit} +/- {uncertainty}")

    fit_results = [combined_fit_results]
    if args.fit_comparisons:
        for workspace in workspaces:
            fit_results.append(workspace.fit_results())

    output_folder = pathlib.Path(args.output_dir)
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
    elif not output_folder.is_dir():
        raise ValueError("Provided path {args.output_dir} is not a folder. Cannot create directory.")
    figure_folder = output_folder / "figures"
    if not figure_folder.exists():
        figure_folder.mkdir()
    logger.debug("Creating pull plot.")
    common.plotting.pull_plot(fit_results=combined_fit_results, figure_folder=figure_folder)
    logger.debug("Creating correlation matrix.")
    common.plotting.correlation_matrix(fit_results=combined_fit_results, figure_folder=figure_folder, pruning_threshold=0.1)
    logger.debug("Creating normalisation factor plot.")
    model_names = [combined_ws.name]
    model_names.extend([analysis_name for analysis_name in args.analysis_names])
    common.plotting.norm_factors(fit_results=fit_results, figure_folder=figure_folder, model_names=model_names)

    logger.debug("Evaluating exclusion limits.")
    combined_limit_results = combined_ws.limit_results()
    limit_results = [combined_limit_results]
    if args.fit_comparisons:
        limit_results.extend([ws.limit_results() for ws in workspaces])
        common.plotting.limit_comparison(limit_results=limit_results, figure_folder=figure_folder, model_names=model_names)
    
    if args.ranking:
        logger.debug("Creating ranking plot.")
        common.plotting.ranking(ranking_results=combined_ws.ranking_results(), figure_folder=figure_folder)
    
if __name__ == "__main__":
    main()