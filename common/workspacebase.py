import functools

import pyhf
import cabinetry

import common.limits

from common.logger import logger


class WorkspaceBase:
    def __init__(self, name: str, ws: pyhf.Workspace):
        self.name = name
        self.ws = ws

    @property
    def _measurement(self):
        return self.ws.get_measurement()

    @property
    def _model_spec(self):
        return {
            "channels": self.ws["channels"],
            "parameters": self._measurement["config"]["parameters"],
        }

    @property
    def _model(self):
        return pyhf.pdf.Model(self._model_spec, poi_name="SigXsecOverSM")

    @property
    def _data(self):
        return self.ws.data(self._model, include_auxdata=True)

    @functools.lru_cache
    def fit_results(self):
        logger.debug(f"Starting fit for workspace {self.name}.")
        return cabinetry.fit.fit(self._model, self._data)

    def ranking_results(self):
        logger.debug(f"Starting ranking for workspace {self.name}.")
        return cabinetry.fit.ranking(
            model=self._model, data=self._data, fit_results=self.fit_results()
        )

    def limit_results(self):
        logger.debug(f"Starting limit setting for workspace {self.name}.")
        # return cabinetry.fit.limit(model=self._model, data=self._data)
        return common.limits.limit_customScan(self._model, self._data)
