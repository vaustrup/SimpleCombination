import functools
import logging

import pyhf
import cabinetry

logger = logging.getLogger("SimpleCombination")

class WorkspaceBase:
    def __init__(self, ws: pyhf.Workspace):
        self.ws = ws

    @property
    def _measurement(self):
        return self.ws.get_measurement()
    
    @property
    def _model_spec(self):
        return {
            'channels': self.ws["channels"],
            'parameters': self._measurement['config']['parameters']
        }
    
    @property
    def _model(self):
        return pyhf.pdf.Model(self._model_spec, poi_name="SigXsecOverSM")
    
    @property
    def _data(self):
        return self.ws.data(self._model, include_auxdata=True)

    @functools.lru_cache
    def fit_results(self):
        logger.info("Starting fit on combined workspace.")
        return cabinetry.fit.fit(self._model, self._data)

    def ranking_results(self):
        return cabinetry.fit.ranking(model=self._model, data=self._data, fit_results=self.fit_results())
    
    def limit_results(self):
        return cabinetry.fit.limit(model=self._model, data=self._data)
    