import pytest
from fastmcp import Client
import nest_asyncio

nest_asyncio.apply()


@pytest.mark.asyncio
async def test_kb(kb_mcp_fixture):
    async with Client(kb_mcp_fixture) as client:
        # Test create_notebook
        result = await client.call_tool("kb_list_workflows", {})
        assert "decoupler" in result.content[0].text

        result = await client.call_tool(
            "kb_show_workflow",
            {"filename": "decoupler_scRNA_TF_Activity_Scoring_Workflow.md"},
        )
        assert "CollecTRI" in result.content[0].text
