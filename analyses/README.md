# Analysis-specific Configuration

All settings available for analysis-specific configuration are defined in the abstract base class `AnalysisBase`.
Analysis configuration classes inherit from this base class. 
Users are required to overwrite the methods `filename` and `signalname`, which return the name of the file containing the workspace and the name of the signal process within this workspace, respectively. In these functions, users have access to parameters defined on the command-line when running with the `-p` option, e.g. `combine.py -p mass=1300`. These parameters are available in a dictionary by using `self.parameters[key]`.
All other settings can be overwritten but are not required. The simplest analysis configuration file therefore looks like

```python
from common.analysisbase import AnalysisBase


class Analysis(AnalysisBase):
    def filename(self):
        return "analysis.json"

    def signalname(self):
        return "signal"
```

Additional settings can be used to prune systematic uncertainties or to rename samples. They are detailed in the following.

- `modifiers_to_prune`:
    
    A dictionary with sample name as key and list of modifier names to prune for given sample as value

        modifiers_to_prune = {
            'foo': ['bar', 'quu*'],
            'baz': ['qux'],
        }

    Supports regex matching for sample names and for modifier names.
    This will prune modifiers matching `bar` or `quu*` in samples matching `foo` and modifiers matching `qux` in samples matching `baz`.

- `modifiers_to_rename`:
    A dictionary mapping old modifier names to new modifier names can be provided in the child class in the form

        modifiers_to_rename = {
            'foo': 'bar',
            'baz': 'qux',
        }

    This will rename the modifier `foo` into `bar` and the modifier `baz` into `qux`.

- `samples_to_rename`:
  A dictionary mapping old sample names to new sample names can be provided in the child class in the form

        samples_to_rename = {
            'foo': 'bar',
            'baz': 'qux',
        }

    This will rename the sample `foo` into `bar` and the sample `baz` into `qux`.