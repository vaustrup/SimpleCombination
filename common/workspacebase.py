import functools

import pyhf
import cabinetry

import common.limitsetting

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
    def model(self):
        return pyhf.pdf.Model(self._model_spec, poi_name="SigXsecOverSM")

    @property
    def _data(self):
        return self.ws.data(self.model, include_auxdata=True)

    @functools.lru_cache
    def fit_results(self):
        logger.debug(f"Starting fit for workspace {self.name}.")
        return cabinetry.fit.fit(self.model, self._data)

    def ranking_results(self):
        logger.debug(f"Starting ranking for workspace {self.name}.")
        return cabinetry.fit.ranking(
            model=self.model, data=self._data, fit_results=self.fit_results()
        )

    def limit_results(self, method: str = "default"):
        method = method.lower()
        if method not in ["default", "bisect"]:
            raise ValueError(
                f"Method '{method}' chosen for limit setting \
                             is not valid. \
                             Available methods are 'default' and 'bisect'."
            )
        logger.debug(
            f"Starting limit setting for workspace {self.name} \
                using method '{method}'."
        )
        if method == "bisect":
            return common.limitsetting.limit_customScan(self.model, self._data)
        return cabinetry.fit.limit(model=self._model, data=self._data)

    def correlate_NPs(self, correlated_NPs: dict[str, dict]) -> None:
        for new_name, old_names in correlated_NPs.items():
            if not self.name in old_names:
                continue
            old_name = f"{old_names[self.name]}_{self.name}"
            if not old_name in self.ws.model().config.parameters:
                logger.warning(
                    f"Cannot correlate NP {old_name}, \
                               not found in list of model parameters for \
                               analysis {self.name}."
                )
                continue
            self.ws = self.ws.rename({old_name: new_name})
