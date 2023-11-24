import logging

import pyhf

from common.workspacebase import WorkspaceBase
from common.workspace import Workspace

from typing import List

logger = logging.getLogger("SimpleCombination")

class CombinedWorkspace(WorkspaceBase):

    def __init__(self, name: str, workspaces: List[Workspace]):
        self.name = name
        self.workspaces = workspaces
        self.ws = self._combine_workspaces(workspaces)

    @staticmethod
    def _combine_workspaces(workspaces: List[Workspace] ):
        ws = workspaces[0].ws
        if len(workspaces) == 1:
            logger.info("There is only one workspace. Nothing to combine.")
            return ws
        for i_ws in range(1, len(workspaces)):
            ws = pyhf.Workspace.combine(ws, workspaces[i_ws].ws, join="outer", merge_channels=True)
        logger.info(f"Combined {len(workspaces)} workspaces.")
        return ws
