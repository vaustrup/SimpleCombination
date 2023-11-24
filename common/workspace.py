import re

import pyhf

from common.workspacebase import WorkspaceBase
import common.utils

from typing import Dict, List

class Workspace(WorkspaceBase):
    """
    Class providing helper methods to modify pyhf.Workspaces.
    """

    def __init__(self, name: str, ws: pyhf.Workspace):
        self.name = name
        self.ws: pyhf.Workspace = ws

    def mark_regions(self) -> None:
        """
        Ensure names of regions are unique by appending the name of the individual analysis.
        """
        self.ws = self.ws.rename(channels={channel: f"{channel}_{self.name}" for channel in self.ws.model().config.channels})

    def mark_modifiers(self) -> None:
        """
        Ensure names of modifiers are unique by appending the name of the individual analysis.
        """
        modifiers = {}
        for modifier in self.ws.model().config.parameters:
            if modifier == "lumi":
                continue # renaming the lumi modifier breaks assumptions of pyhf
            if modifier == self.ws.get_measurement()["config"]["poi"]:
                continue # do not rename POI
            modifiers[modifier] = modifier + "_" + self.name.replace(" ", "")
        self.rename_modifiers(names=modifiers)

    def prune_modifiers(self, modifiers_to_prune: Dict[str, List[str]]) -> None:
        """
        Remove modifiers from workspace for certain samples.

        Arguments:
            modifiers_to_prune (Dict[str, List[str]]): dictionary with sample name as key and list of modifiers to prune as value
        """
        for i_channel, channel in enumerate(self.ws["channels"]):
            for i_sample, sample in enumerate(channel["samples"]):
                for prune_sample, prune_tags in modifiers_to_prune.items():
                    if not re.match(prune_sample, sample["name"]): continue
                    
                    # position of modifier to prune is appended to list
                    prune_modifiers: List[int] = []
                    for i_modifier, modifier in enumerate(sample["modifiers"]):
                        # skip if already added to list when it matches multiple pruning tags
                        if i_modifier in prune_modifiers: continue

                        for prune_tag in prune_tags:
                            if not re.match(prune_tag, modifier["name"]): continue
                            prune_modifiers.append(i_modifier)

                    # delete in reverse to avoid problems with indeces
                    for i in sorted(prune_modifiers, reverse=True):
                        del self.ws["channels"][i_channel]["samples"][i_sample]["modifiers"][i]

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

    def rename_samples(self, names: Dict[str, str]) -> None:
        """
        Rename sample names.

        Arguments:
            names (Dict[str, str]): dictionary with old sample names as key and new samples names as value
        """
        self.ws = self.ws.rename(samples=names)

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
