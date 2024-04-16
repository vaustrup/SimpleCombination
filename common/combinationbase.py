from abc import ABC
from dataclasses import dataclass


@dataclass
class CombinationBase(ABC):
    """
    Base class for combination configuration settings
    from which all individual combination classes should inherit.
    Default settings are provided by CombinationBase,
    which can be overridden in child classes.
    """

    name: str

    # Name of the output directory, in which to save all results,
    # can be specified in the child class with
    # outputdir = '/path/to/output/directory'
    outputdir: str | None = None

    # Name of signal process to use in combined workspaces
    # Signal processes in individual workspaces will be renamed to this
    signalname: str = "signal"

    # unfortunately we cannot use channels = {...}
    # so we have to make do with the getter here
    # and override it with a dict in the child class
    @property
    def channels(self):
        """
        A dictionary mapping channel identifier in each analysis
        to channel names as they appear in e.g. plots can be provided
        in the child class as

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
        If no such dictionary is provided, all channels are kept.
        Otherwise channels will be removed
        if they do not appear in the dictionary.
        """
        return None

    # unfortunately we cannot use measurement_parameters = {...}
    # so we have to make do with the getter here
    # and override it with a dict in the child class
    @property
    def measurement_parameters(self):
        """
        A dictionary of measurement parameters to modify settings for
        can be provided in the child class as

        measurement_parameters = {
            'parameter1': {'setting1': 'foo'},
            'parameter2': {'setting1': 'bar'}
        }

        These modifications are applied to all individual analysis workspaces.
        """
        return {}

    # unfortunately we cannot use correlated_NPs = {...}
    # so we have to make do with the getter here
    # and override it with a dict in the child class
    @property
    def correlated_NPs(self):
        """
        A dictionary of nuisance parameters to correlate across analyses
        can be provided in the child class as

        correlated_NPs = {
            'np1': {'analysis1': 'foo', 'analysis2': 'bar'},
            'np2': {'analysis1': 'baz', 'analysis2': 'qux'}
        }

        where 'np1' and 'np2' are the names of the correlated NPs
        in the combined workspace, and their corresponding names in the
        individual input workspaces are given as key-value pairs with
        the analysis name as key and the name of the NP to be correlated
        as value
        """
        return {}
