from pathlib import Path
from typing import Any, Dict

from fastmcp import FastMCP

mcp = FastMCP(name="SimpleMCPTestServer")

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def resolve_abs_path(path_str: str) -> Path:
    """
    file.py -> /Users/home/mihail/modern-software-dev-lectures/file.py
    """
    path = Path(path_str).expanduser()
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    return path

@mcp.tool
def read_file_tool(filename: str) -> Dict[str, Any]:
    """
    Gets the full content of a file provided by the user.
    :param filename: The name of the file to read.
    :return: The full content of the file.
    """
    full_path = resolve_abs_path(filename)
    print(full_path)

    if not full_path.is_file():
        return {"error": f"Not a valid file: {full_path}"}

    if full_path.stat().st_size > MAX_FILE_SIZE:
        return {"error": f"File too large: {full_path}"}

    try:
        with open(str(full_path), "r") as f:
            content = f.read()
    except PermissionError:
        return {"error": f"Permission denied: {full_path}"}
    except UnicodeDecodeError:
        return {"error": f"File is not valid text: {full_path}"}

    return {
        "file_path": str(full_path),
        "content": content
    }

@mcp.tool
def list_files_tool(path: str) -> Dict[str, Any]:
    """
    Lists the files in a directory provided by the user.
    :param path: The path to the directory to list files from.
    :return: A list of files in the directory.
    """
    full_path = resolve_abs_path(path)
    all_files = []
    for item in full_path.iterdir():
        all_files.append({
            "filename": item.name,
            "type": "file" if item.is_file() else "dir"
        })
    return {
        "path": str(full_path),
        "files": all_files
    }

@mcp.tool
def edit_file_tool(path: str, old_str: str, new_str: str) -> Dict[str, Any]:
    """
    Replaces first occurrence of old_str with new_str in file. If old_str is empty, creates/overwrites file with new_str.
    :param path: The path to the file to edit.
    :param old_str: The string to replace.
    :param new_str: The string to replace with.
    :return: A dictionary with the path to the file and the action taken.
    """
    full_path = resolve_abs_path(path)
    p = Path(full_path)
    if old_str == "":
        p.write_text(new_str, encoding="utf-8")
        return {
            "path": str(full_path),
            "action": "created_file"
        }
    original = p.read_text(encoding="utf-8")
    if original.find(old_str) == -1:
        return {
            "path": str(full_path),
            "action": "old_str not found"
        }
    edited = original.replace(old_str, new_str, 1)
    p.write_text(edited, encoding="utf-8")
    return {
        "path": str(full_path),
        "action": "edited"
    }

#  We can test this MCP server with Claude Desktop (acting as the MCP client):
#
# 1. Add the following to claude_desktop_config.json
#    (on macOS: ~/Library/Application Support/Claude/claude_desktop_config.json):
#
#    "mcpServers": {
#      "simple-mcp": {
#        "command": "<path-to-virtualenv>/bin/python",
#        "args": ["<path-to>/simple_mcp.py"]
#      }
#    }
#
#    Use the virtualenv Python so that dependencies (e.g. fastmcp) are available.
#
# 2. Restart Claude Desktop. The tools (read_file_tool, list_files_tool,
#    edit_file_tool) should appear in the chat.
#
# 3. Remove the mcpServers config when done testing.

if __name__ == "__main__":
    mcp.run()