from common.misc.utils import *


def test_parse_parameters_returns_empty():
    args = parse_parameters(parameter_list=None)
    assert args == {}


def test_parse_parameters_returns_dict():
    parameter_list = ["a=1", "f=x"]
    args = parse_parameters(parameter_list=parameter_list)
    parameter_dict = {"a": "1", "f": "x"}
    assert args == parameter_dict
