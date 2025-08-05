from fastmcp import FastMCP

kb_mcp = FastMCP("KB-Server")


@kb_mcp.tool(tags={"kb"})
def list_workflows():
    """list all workflows"""
    from ..kb import ls_workflows

    return ls_workflows()


@kb_mcp.tool(tags={"kb"})
def show_workflow(filename: str):
    """show a workflow"""
    from ..kb import read_workflow

    return read_workflow(filename)
