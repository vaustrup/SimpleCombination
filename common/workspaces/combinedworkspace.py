import pyhf

from common.workspaces.workspacebase import WorkspaceBase
from common.workspaces.workspace import Workspace

from common.misc.logger import logger


class CombinedWorkspace(WorkspaceBase):
    def __init__(self, name: str, workspaces: list[Workspace]):
        self.name = name
        self.workspaces = workspaces
        self.ws = self._combine_workspaces(workspaces)

    @staticmethod
    def _combine_workspaces(workspaces: list[Workspace]):
        ws = workspaces[0].ws
        if len(workspaces) == 1:
            logger.info("There is only one workspace. Nothing to combine.")
            return ws
        for i_ws in range(1, len(workspaces)):
            ws = pyhf.Workspace.combine(
                ws, workspaces[i_ws].ws, join="outer", merge_channels=True
            )
        logger.info(f"Combined {len(workspaces)} workspaces.")
        return ws
