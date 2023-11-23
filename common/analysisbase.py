from abc import ABC, abstractmethod
from dataclasses import dataclass
import json

import pyhf

from common.workspace import Workspace
from common.combinationbase import CombinationBase

import logging

from typing import Dict, List, Optional

@dataclass
class AnalysisBase(ABC):
    """
    Base class for analysis configuration settings from which all individual analysis classes should inherit.
    Child classes are required to implement certain methods (filename, signalname) and additionally can override other default settings.
    """
    name: str
    parameters: Dict[str, str]
    _logger = logging.getLogger("SimpleCombination")

    
    @property
    def modifiers_to_prune(self) -> Dict[str, List[str]]:
        """
        A dictionary with sample name as key and list of modifier names to prune for given sample as value

        modifiers_to_prune = {
            'foo': ['bar', 'quu*'],
            'baz': ['qux'],
        }
        
        supports regex matching for sample names and for modifier names
        """
        return {}

    @property
    def samples_to_rename(self) -> Dict[str, str]:
        """
        A dictionary mapping old sample names to new sample names can be provided in the child class in the form

        samples_to_rename = {
            'foo': 'bar',
            'baz': 'qux',
        }
        """
        return {}
    
    @property
    def modifiers_to_rename(self) -> Dict[str, str]:
        """
        A dictionary mapping old modifier names to new modifier names can be provided in the child class in the form

        modifiers_to_rename = {
            'foo': 'bar',
            'baz': 'qux',
        }
        """
        return {}

    @abstractmethod
    def filename(self, p: dict) -> str:
        """
        A function returning the name of the file containing the workspace based on given parameters needs to be defined in the child class.
        """
        raise NotImplementedError("Function returning name of file containing workspace has not been defined. Add 'def filename(self):' to the analysis {self.name}.")

    @abstractmethod
    def signalname(self, p: dict) -> str:
        """
        A function returning the name of the signal process based on given parameters needs to be defined in the child class.
        """
        raise NotImplementedError("Function returning name of signal process has not been defined. Add 'def signalname(self):' to the analysis {self.name}.")

    def _modify_workspace(self, workspace: Workspace, parameters: Dict, combination: Optional[CombinationBase]=None) -> Workspace:
        """
        Modify workspace according to setting in analysis and combination configuration classes.

        Arguments:
            workspace (Workspace): Workspace instance containing pyhf.Workspace to modify
            combination (Optional[CombinationBase]): Instance of given combination configuration class inheriting from CombinationBase (default: None)
        
        Returns modified Workspace instance.

        Do not override.
        """
        self._logger.info(f"Modify workspace for analysis {self.name}.")
        workspace.rename_measurement()
        workspace.rename_poi()
        workspace.prune_modifiers(self.modifiers_to_prune)
        
        if combination is not None:
            self._logger.info(f"Apply settings for combination {combination.name}.")
            if combination.channels is not None: workspace.prune_regions(combination.channels[self.name].keys())
            workspace.set_measurement_parameters(combination.measurement_parameters)
            # rename signal process to common name for combined workspaces
            workspace.rename_samples( {self.signalname(): combination.signalname} )
        
        workspace.mark_regions()
        workspace.mark_modifiers()
        
        return workspace

    def workspace(self, parameters: Dict, combination: Optional[CombinationBase]=None) -> pyhf.Workspace:
        """
        Read pyhf.Workspace from input file and modify it according to settings in analysis and combination configuration classes.

        Arguments:
            combination (Optional[CombinationBase]): Instance of given combination configuration class inheriting from CombinationBase (default: None)

        Returns pyhf.Workspace object after applying modifications

        Do not override.
        """
        filename = self.filename()
        
        with open(filename, "r") as f:
            try:
                spec = json.load(f)
            except json.decoder.JSONDecodeError:
                raise ValueError(f"Input file {filename} for analysis {self.name} is not valid JSON.")
        
        workspace = Workspace(name=self.name, ws=pyhf.Workspace(spec))
        workspace = self._modify_workspace(workspace, parameters, combination)
        return workspace.ws
        