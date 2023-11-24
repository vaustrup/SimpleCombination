import argparse
import importlib
import inspect
import pathlib
import logging
import sys

import cabinetry

from common.analysisbase import AnalysisBase
from common.combinationbase import CombinationBase
from common.combinedworkspace import CombinedWorkspace
import common.plotting

import common.utils

logger = logging.getLogger("SimpleCombination")

from typing import Dict, Optional

def get_combination(combination_name: Optional[str]) -> Optional[CombinationBase]:
    """
    Retrieve configuration class for given combination.

    Arguments:
        combination_name (Optional[str]): name of combination

    Returns instance of configuration class. Returns None if combination_name is None.

    Raises:
        AttributeError if module combination.combination_name does not contain a class called 'Combination'.
    """
    if combination_name is None:
        return None
    combination_module = importlib.import_module(f"combinations.{combination_name}")
    # make sure the loaded module actually contains a class called 'Combination'
    if not hasattr(combination_module, "Combination"):
        raise AttributeError(f"Module combinations.{combination_name} does not have an attribute called 'Combination'.")
    if not inspect.isclass(getattr(combination_module, "Combination")):
        raise AttributeError(f"Module combinations.{combination_name} does not have contain a class called 'Combination'.")
    # now we can finally create an instance of the Combination class
    combination = combination_module.Combination(combination_name)
    logger.info(f"Loaded configuration for combination {combination_name}.")
    return combination

def get_analysis_workspace(analysis_name: str, parameters: Dict, combination: Optional[CombinationBase]) -> AnalysisBase:
    """
    Retrieve analysis workspace modified according to settings in configuration class for given analysis.

    Arguments:
        analysis_name (str): name of analysis
        parameters (Dict): dictionary containing parameters to propagate to analysis settings
        combination (Optional[CombinationBase]): instance of combination configuration class

    Returns modified pyhf.Workspace

    Raises:
        AttributeError if module analysis.analysis_name does not contain a class called 'Analysis'.
    """
    analysis_module = importlib.import_module(f"analyses.{analysis_name}")
    # make sure the loaded module actually contains a class called 'Analysis'
    if not hasattr(analysis_module, "Analysis"):
        raise AttributeError(f"Module analysis.{analysis_name} does not have an attribute called 'Analysis'.")
    if not inspect.isclass(getattr(analysis_module, "Analysis")):
        raise AttributeError(f"Module analysis.{analysis_name} does not have contain a class called 'Analysis'.")
    # now we can finally create an instance of the Analysis class
    analysis = analysis_module.Analysis(analysis_name, parameters)
    logger.info(f"Loaded configuration for analysis {analysis_name}.")
    return analysis.workspace(parameters, combination)

def main():
    """
    Combine pyhf workspaces and run statistical evaluations.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--analyses",
                        nargs='+',
                        required=True,
                        dest="analysis_names",
                        help="Whitespace-separated list of analyses to combined."
                        )
    parser.add_argument("-p", "--parameters",
                        nargs='+',
                        dest="parameters",
                        help="Whitespace-separated list of key-value pairs to be used as parameters."
                        )
    parser.add_argument("-c", "--combination",
                        dest="combination_name",
                        help="Name of combination to perform.")
    parser.add_argument("-o", "--output-dir",
                        dest="output_dir",
                        default="output",
                        help="Directory to store output in.")
    parser.add_argument("--output-level",
                        dest="output_level",
                        type=int,
                        default=20,
                        help="Output level for printing logging messages. 10: DEBUG, 20: INFO, 30: WARNING, 40: ERROR, 50: CRITICAL (default: 20)."
                        )
    parser.add_argument("--ranking",
                        dest="ranking",
                        action='store_true',
                        help="Set flag to obtain ranking plot."
                        )
    parser.add_argument("--fit-comparisons",
                        dest="fit_comparisons",
                        action='store_true',
                        help="Set flag to run fits for individual analyses and compare with combined results.")
    
    args = parser.parse_args()

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter("%(asctime)s [%(levelname)4s]: %(message)s", "%d.%m.%Y %H:%M:%S")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(args.output_level)

    parameters = common.utils.parse_parameters(args.parameters)

    combination = get_combination(args.combination_name)
    workspaces = [get_analysis_workspace(analysis_name=analysis_name, parameters=parameters, combination=combination) for analysis_name in args.analysis_names]

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
    cabinetry.visualize.pulls(fit_results=combined_fit_results, figure_folder=figure_folder)
    logger.debug("Creating correlation matrix.")
    cabinetry.visualize.correlation_matrix(fit_results=combined_fit_results, figure_folder=figure_folder, pruning_threshold=0.1)
    logger.debug("Creating normalisation factor plot.")
    model_names = [combined_ws.name]
    model_names.extend([analysis_name for analysis_name in args.analysis_names])
    common.plotting.norm_factors(fit_results=fit_results, figure_folder=figure_folder, model_names=model_names)

    logger.debug("Evaluating exclusion limits.")
    limit_results = combined_ws.limit_results()
    
    if args.ranking:
        logger.debug("Creating ranking plot.")
        cabinetry.visualize.ranking(ranking_results=combined_ws.ranking_results(), figure_folder=figure_folder)
    
if __name__ == "__main__":
    main()