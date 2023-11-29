import argparse

from typing import Optional

from common.logger import logger


def parse_parameters(parameter_list: Optional[list[str]]) -> dict:
    """
    Split parameters provided as a list of strings
    representing key-value pairs separated by a equal-sign.

    Arguments:
        parameter_list (Optional[list[str]]):
            list of strings containing key-value pairs separated by =

    Returns:
        dictionary of parameters,
            with the name as key and the value as value.
        an empty dictionary if parameter_list is None.
    """
    if parameter_list is None:
        logger.debug("No parameters provided. Returning empty dictionary.")
        return {}

    parameter_dict = {}
    for parameter in parameter_list:
        k, v = parameter.split("=")
        parameter_dict[k] = v
    logger.debug(f"Parsed {len(parameter_list)} parameters.")
    return parameter_dict


def get_parameter_index_in_measurement(
    measurement: dict, parameter_name: str
) -> int:
    """
    Finds index of parameter with given name in list stored in measurement.

    Arguments:
        measurement (dict): measurement obtained from pyhf.Workspace
        parameter_name (string): name of parameter to find index of

    Returns index of parameter in list in measurement as int

    Raises:
        ValueError:
            if parameter with name 'parameter_name' is not found in measurement
    """
    for i_parameter, parameter in enumerate(
        measurement["config"]["parameters"]
    ):
        if parameter["name"] == parameter_name:
            return i_parameter

    raise ValueError("Could not find parameter with name {parameter_name}.")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-a",
        "--analyses",
        nargs="+",
        required=True,
        dest="analysis_names",
        help="Whitespace-separated list of analyses to combined.",
    )
    parser.add_argument(
        "-p",
        "--parameters",
        nargs="+",
        dest="parameters",
        help="Whitespace-separated list of key-value pairs \
                to be used as parameters.",
    )
    parser.add_argument(
        "-c",
        "--combination",
        dest="combination_name",
        help="Name of combination to perform.",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="Directory to store output in.",
    )
    parser.add_argument(
        "--output-level",
        dest="output_level",
        type=int,
        default=20,
        help="Output level for printing logging messages. \
                10: DEBUG, 20: INFO, 30: WARNING, \
                40: ERROR, 50: CRITICAL (default: 20).",
    )
    parser.add_argument(
        "--ranking",
        dest="ranking",
        action="store_true",
        help="Set flag to obtain ranking plot.",
    )
    parser.add_argument(
        "--fit-comparisons",
        dest="fit_comparisons",
        action="store_true",
        help="Set flag to run fits for individual analyses \
                and compare with combined results.",
    )

    args = parser.parse_args()

    return args
