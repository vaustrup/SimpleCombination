import pathlib
import sys

from common.workspaces import CombinedWorkspace
import common.misc.helpers
import common.plotting
import common.misc.utils
from common.misc.logger import logger


def main():
    """
    Combine pyhf workspaces and run statistical evaluations.
    """

    args = common.misc.utils.parse_arguments()
    parameters = common.misc.utils.parse_parameters(args.parameters)

    # create output directory based on given parameters
    parameter_string = "_".join(
        [k + v.replace(".", "p") for k, v in parameters.items()]
    )
    output_folder = pathlib.Path(args.output_dir) / parameter_string
    if not output_folder.exists():
        output_folder.mkdir(parents=True)
    elif not output_folder.is_dir():
        raise ValueError(
            "Provided path {args.output_dir} is not a folder. \
                Cannot create directory."
        )

    # configure logger
    file_handler = logger.FileHandler(
        f"{args.output_dir}/{args.combination_name}_output.log"
    )
    stream_handler = logger.StreamHandler(sys.stdout)
    formatter = logger.Formatter(
        "%(asctime)s [%(levelname)4s]: %(message)s", "%H:%M:%S"
    )
    stream_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    logger.basicConfig(
        handlers=[file_handler, stream_handler], level=args.output_level
    )

    # now we can finally do the actual combination
    # start by obtaining the combination settings
    # and the individual workspaces
    combination = common.misc.helpers.get_combination(args.combination_name)
    workspaces = [
        common.misc.helpers.get_analysis_workspace(
            analysis_name=analysis_name,
            parameters=parameters,
            combination=combination,
        )
        for analysis_name in args.analysis_names
    ]

    figure_folder = output_folder / "figures"
    if not figure_folder.exists():
        figure_folder.mkdir()

    combined_ws = CombinedWorkspace(name="Combined", workspaces=workspaces)
    common.plotting.modifier_grid(
        model=combined_ws.model, figure_folder=figure_folder
    )
    combined_fit_results = combined_ws.fit_results()
    with open(output_folder / "fit_results.txt", "w") as f:
        for label, bestfit, uncertainty in zip(
            combined_fit_results.labels,
            combined_fit_results.bestfit,
            combined_fit_results.uncertainty,
        ):
            np = f"{label}: {bestfit} +/- {uncertainty}"
            logger.debug(np)
            f.write(f"{np}\n")

    fit_results = [combined_fit_results]
    if args.fit_comparisons:
        for workspace in workspaces:
            fit_results.append(workspace.fit_results())

    logger.debug("Creating pull plot.")
    common.plotting.pull_plot(
        fit_results=combined_fit_results, figure_folder=figure_folder
    )
    logger.debug("Creating correlation matrix.")
    common.plotting.correlation_matrix(
        fit_results=combined_fit_results,
        figure_folder=figure_folder,
        pruning_threshold=0.1,
    )
    logger.debug("Creating normalisation factor plot.")
    model_names = [combined_ws.name]
    model_names.extend([analysis_name for analysis_name in args.analysis_names])
    common.plotting.norm_factors(
        fit_results=fit_results,
        figure_folder=figure_folder,
        model_names=model_names,
    )

    logger.debug("Evaluating exclusion limits.")
    combined_limit_results = combined_ws.limit_results(args.limit_method)
    limit_results = [combined_limit_results]
    if args.fit_comparisons:
        limit_results.extend(
            [ws.limit_results(args.limit_method) for ws in workspaces]
        )
        common.plotting.limit_comparison(
            limit_results=limit_results,
            figure_folder=figure_folder,
            model_names=model_names,
        )

    if args.ranking:
        logger.debug("Creating ranking plot.")
        common.plotting.ranking(
            ranking_results=combined_ws.ranking_results(),
            figure_folder=figure_folder,
        )


if __name__ == "__main__":
    main()
