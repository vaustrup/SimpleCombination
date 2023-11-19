import functools

import pyhf

from typing import List

class CombinedWorkspace:

    def __init__(self, workspaces: List[pyhf.Workspace]):
        self.workspaces = workspaces
        self.ws = self._combine_workspaces(workspaces)

    @staticmethod
    def _combine_workspaces(workspaces: List[pyhf.Workspace] ):
        ws = workspaces[0]
        if len(workspaces) == 1:
            return ws
        for i_ws in range(1, len(workspaces)):
            ws = pyhf.Workspace.combine(ws, workspaces[i_ws], join="outer", merge_channels=True)
        return ws

    @functools.lru_cache
    def fit_results(self):
        measurement = self.ws.get_measurement()
        model_spec = {
            'channels': self.ws["channels"],
            'parameters': measurement['config']['parameters']
        }
        model = pyhf.pdf.Model(model_spec, poi_name=args.poi_name)
        data = self.ws.data(model, include_auxdata=True)

        fit_results = cabinetry.fit.fit(model, data)
        return fit_results
