from typing import List, Optional

def parse_parameters(parameter_list: Optional[List[str]]) -> dict:
    """
    Split parameters provided as a list of strings representing key-value pairs separated by a equal-sign.

    Arguments:
        parameter_list (Optional[List[str]]): list of strings containing key-value pairs separated by =.

    Returns dictionary of parameters, with the name as key and the value as value. Returns an empty dictionary if parameter_list is None.
    """
    if parameter_list is None:
        return {}
    
    parameter_dict = {}
    for parameter in parameter_list:
        k, v = parameter.split("=")
        parameter_dict[k] = v
    return parameter_dict

def get_parameter_index_in_measurement(measurement, parameter_name) -> int:
    """
    Finds index of parameter with given name in list stored in measurement.

    Arguments:
        measurement (Dict): measurement obtained from pyhf.Workspace
        parameter_name (string): name of parameter to find index of

    Returns index of parameter in list in measurement as int

    Raises:
        ValueError when parameter with name 'parameter_name' is not found in measurement
    """
    for i_parameter, parameter in enumerate(measurement["config"]["parameters"]):
        if parameter["name"] == parameter_name:
            return i_parameter
    
    raise ValueError("Could not find parameter with name {parameter_name}.")
