from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class CombinationBase(ABC):
    """
    Base class for combination configuration settings from which all individual combination classes should inherit.
    Default settings are provided by CombinationBase, which can be overridden in child classes.
    """

    @property
    def outputdir(self):
        """
        Name of the output directory, in which to save all results, can be specified in the child class with

        outputdir = '/path/to/output/directory'
        """
        return None
    
    @property
    def channels(self):
        """
        A dictionary mapping channel identifier in each analysis to channel names as they appear in e.g. plots can be provided in the child class as

        channels = {
            'analysis1': {
                'foo': 'bar',
                'baz': 'qux',
            },
            'analysis2': {
                'quux': 'corge',
                'grault': 'garply',
            }
        }
        If no such dictionary is provided, all channels are kept. Otherwise channels will be removed if they do not appear in the dictionary.
        """
        return None
    
    @property
    def measurement_parameters(self):
        """
        A dictionary of measurement parameters to modify settings for can be provided in the child class as

        measurement_parameters = {
            'parameter1': {'setting1': 'foo'}
            'parameter2': {'setting1': 'bar'}
        }
        
        These modifications are applied to all individual analysis workspaces.
        """
        return {}