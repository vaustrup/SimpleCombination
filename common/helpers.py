import importlib
import inspect

from common.combinationbase import CombinationBase
from common.workspace import Workspace

from typing import Dict, Optional

from common.logger import logger


def get_combination(
    combination_name: Optional[str],
) -> Optional[CombinationBase]:
    """
    Retrieve configuration class for given combination.

    Arguments:
        combination_name (Optional[str]):
            name of combination

    Returns instance of configuration class.
    Returns None if combination_name is None.

    Raises:
        AttributeError:
            if module combination.combination_name
            does not contain a class called 'Combination'.
    """
    if combination_name is None:
        return None
    combination_module = importlib.import_module(
        f"combinations.{combination_name}"
    )
    # make sure the loaded module actually
    # contains a class called 'Combination'
    if not hasattr(combination_module, "Combination"):
        raise AttributeError(
            f"Module combinations.{combination_name} \
                does not have an attribute called 'Combination'."
        )
    if not inspect.isclass(getattr(combination_module, "Combination")):
        raise AttributeError(
            f"Module combinations.{combination_name} \
                does not have contain a class called 'Combination'."
        )
    # now we can finally create an instance of the Combination class
    combination = combination_module.Combination(combination_name)
    logger.info(f"Loaded configuration for combination {combination_name}.")
    return combination


def get_analysis_workspace(
    analysis_name: str, parameters: Dict, combination: Optional[CombinationBase]
) -> Workspace:
    """
    Retrieve analysis workspace modified according to settings
    in configuration class for given analysis.

    Arguments:
        analysis_name (str):
            name of analysis
        parameters (Dict):
            dictionary containing parameters to propagate to analysis settings
        combination (Optional[CombinationBase]):
            instance of combination configuration class

    Returns modified pyhf.Workspace

    Raises:
        AttributeError:
            if module analysis.analysis_name
            does not contain a class called 'Analysis'.
    """
    analysis_module = importlib.import_module(f"analyses.{analysis_name}")
    # make sure the loaded module actually contains a class called 'Analysis'
    if not hasattr(analysis_module, "Analysis"):
        raise AttributeError(
            f"Module analysis.{analysis_name} \
                does not have an attribute called 'Analysis'."
        )
    if not inspect.isclass(getattr(analysis_module, "Analysis")):
        raise AttributeError(
            f"Module analysis.{analysis_name} \
                does not have contain a class called 'Analysis'."
        )
    # now we can finally create an instance of the Analysis class
    analysis = analysis_module.Analysis(analysis_name, parameters)
    logger.info(f"Loaded configuration for analysis {analysis_name}.")
    return analysis.workspace(parameters, combination)
