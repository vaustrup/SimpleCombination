# Combination-specific Configuration

All settings available for combination-specific configuration are defined in the abstract base class `CombinationBase`.
Combination configuration classes inherit from this base class.

- `channels`:

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

- `correlated_NPs`:

    A dictionary of nuisance parameters to correlate across analyses can be provided in the child class as

        correlated_NPs = {
            'np1': {'analysis1': 'foo', 'analysis2': 'bar'},
            'np2': {'analysis1': 'baz', 'analysis2': 'qux'}
        }

    where `np1` and `np2` are the names of the correlated NPs in the combined workspace, and their corresponding names in the individual input workspaces are given as key-value pairs with the analysis name as key and the name of the NP to be correlated as value.

- `measurement_parameters`:

    A dictionary of measurement parameters to modify settings for can be provided in the child class as

        measurement_parameters = {
            'parameter1': {'setting1': 'foo'},
            'parameter2': {'setting1': 'bar'}
        }

    These modifications are applied to all individual analysis workspaces.

- `signalname`: 

    Name of signal process to use in combined workspaces. Signal processes in individual workspaces will be renamed to this. Defaults to `signal`.