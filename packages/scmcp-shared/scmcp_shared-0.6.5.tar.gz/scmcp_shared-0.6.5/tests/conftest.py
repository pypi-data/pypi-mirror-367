import pytest
from scmcp_shared.backend import AdataManager
from scmcp_shared.mcp_base import BaseMCPManager, NotebookManager
from scmcp_shared.server.preset import ScanpyIOMCP
from scmcp_shared.server.preset import ScanpyPreprocessingMCP
from scmcp_shared.server.preset import ScanpyToolsMCP
from scmcp_shared.server.preset import ScanpyPlottingMCP
from scmcp_shared.server.preset import ScanpyUtilMCP
from scmcp_shared.server.auto import auto_mcp
from scmcp_shared.server.code import nb_mcp
from scmcp_shared.server.rag import rag_mcp
from scmcp_shared.server.kb import kb_mcp


class ScanpyMCPManager(BaseMCPManager):
    """Manager class for Scanpy MCP modules."""

    def init_mcp(self):
        """Initialize available Scanpy MCP modules."""
        self.available_modules = {
            "io": ScanpyIOMCP().mcp,
            "pp": ScanpyPreprocessingMCP().mcp,
            "tl": ScanpyToolsMCP().mcp,
            "pl": ScanpyPlottingMCP().mcp,
            "ul": ScanpyUtilMCP().mcp,
            "auto": auto_mcp,
            "nb": nb_mcp,
            "rag": rag_mcp,
            "kb": kb_mcp,
        }


@pytest.fixture
def mcp():
    return ScanpyMCPManager("scmcp", backend=AdataManager).mcp


@pytest.fixture
def nb_mcp_fixture():
    mcp = ScanpyMCPManager("scmcp", include_tags=["nb"], backend=NotebookManager).mcp
    return mcp


@pytest.fixture
def kb_mcp_fixture():
    mcp = ScanpyMCPManager("scmcp", include_tags=["kb"], backend=NotebookManager).mcp
    return mcp
