import pyhf

import common.utils

from typing import Dict, List

class Workspace():
    """
    Class providing helper methods to modify pyhf.Workspaces.
    """

    def __init__(self, ws: pyhf.Workspace):
        self.ws: pyhf.Workspace = ws

    def prune_regions(self, regions_to_keep: List[str]) -> None:
        """
        Remove regions from workspace.
        
        Arguments:
            regions_to_keep (List[str]): only regions with name matching one of the strings provided in this list are kept
        """
        prune_regions = [region["name"] for region in self.ws["channels"] if region["name"] not in regions_to_keep]
        self.ws = self.ws.prune(channels=prune_regions)

    def rename_measurement(self, name: str = "Measurement") -> None:
        """
        Rename the measurement to ensure consistency when combining workspaces.
       
        Arguments:
            name (str): New name for the measurement (default: 'Measurement')
        """
        self.ws = self.ws.rename(measurements={self.ws.get_measurement()["name"]: name})

    def rename_modifiers(self, names: Dict[str, str]) -> None:
        """
        Arguments:
            names (Dict[str, str]): dictionary mapping old modifier names to new modifier names
        """
        self.ws = self.ws.rename(modifiers=names)

    def rename_poi(self, poi_name: str = "SigXsecOverSM") -> None:
        """
        Rename POI to ensure consistency when combining workspaces.

        Arguments:
            poi_name (str): new name for POI (default: 'SigXsecOverSM')
        """
        old_poi = self.ws["measurements"][0]["config"]["poi"]
        self.ws["measurements"][0]["config"]["poi"] = poi_name
        self.rename_modifiers({ old_poi: poi_name } )

    def set_measurement_parameters(self, parameters: dict) -> None:
        """
        Modify settings for measurement parameters.

        Arguments:
            parameters (dict): dictionary with names of measurement parameters to modify as keys and dictionary of settings as value
        """
        for parameter, settings in parameters.items():
            i_param = common.utils.get_parameter_index_in_measurement(self.ws.get_measurement(), parameter)
            for setting, value in settings.items():
                self.ws["measurements"][0]["config"]["parameters"][i_param][setting] = value
            if parameter == "lumi" and "fixed" not in settings.keys():
                self.ws["measurements"][0]["config"]["parameters"][i_param].pop( "fixed", None )
