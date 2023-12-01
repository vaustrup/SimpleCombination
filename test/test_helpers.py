from common.misc.helpers import *


def test_get_combination_returns_None():
    c = get_combination(None)
    assert c is None


def test_get_combination_returns_class():
    c = get_combination("combination1")
    assert isinstance(c, CombinationBase)
