import os
import json
from typing import Optional, List, Dict
from fastmcp import FastMCP
from pydantic import Field

util_mcp = FastMCP("Util-Server")


def get_flat_dir_structure(
    path: str, ignore_hidden: bool = True, file_types: Optional[List[str]] = None
) -> Dict[str, Dict[str, List[str]]]:
    structure = {}
    for root, dirs, files in os.walk(path):
        rel_root = os.path.relpath(root, path)
        if rel_root == ".":
            rel_root = ""
        # 过滤隐藏文件和目录
        dirs[:] = [d for d in dirs if not (ignore_hidden and d.startswith("."))]
        if file_types:
            files = [f for f in files if any(f.endswith(ext) for ext in file_types)]
        files = [f for f in files if not (ignore_hidden and f.startswith("."))]
        structure[rel_root] = {"dirs": dirs, "files": files}
    return structure


def get_path_info(
    path: str, ignore_hidden: bool = True, file_types: Optional[List[str]] = None
) -> str:
    if not os.path.exists(path):
        return json.dumps({"error": "路径不存在"}, ensure_ascii=False)
    if os.path.isfile(path):
        if file_types and not any(path.endswith(ext) for ext in file_types):
            return json.dumps({"error": "文件类型不匹配"}, ensure_ascii=False)
        return json.dumps({"type": "file", "path": path}, ensure_ascii=False)
    elif os.path.isdir(path):
        structure = get_flat_dir_structure(path, ignore_hidden, file_types)
        return json.dumps(
            {"type": "directory", "path": path, "structure": structure},
            ensure_ascii=False,
            indent=2,
        )
    else:
        return json.dumps({"error": "未知类型"}, ensure_ascii=False)


@util_mcp.tool(tags={"util"})
def get_path_structure(
    path: str = Field(description="The path to get the structure of"),
) -> str:
    """get the directory structure of a path"""
    return get_path_info(path)
