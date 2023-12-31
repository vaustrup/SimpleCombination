from common.combinationbase import CombinationBase


class Combination(CombinationBase):
    channels = {
        "analysis1": {
            "SR": "SR",
            "CR1": "CR bkg 1",
            "CR2": "CR bkg 2",
        },
        "analysis2": {
            "SR": "SR",
            "CR1": "CR bkg 1",
            "CR2": "CR bkg 2",
        },
    }

    measurement_parameters = {
        "SigXsecOverSM": {"bounds": [[0, 5]], "inits": [0.0], "fixed": False},
        "lumi": {"sigmas": [0.017], "bounds": [[0.915, 1.085]], "fixed": False},
    }

    correlated_NPs = {
        "normsys2": {"analysis1": "normsys2", "analysis2": "normsys2"},
        "histosys1": {"analysis1": "histosys1", "analysis2": "histosys1"},
    }
