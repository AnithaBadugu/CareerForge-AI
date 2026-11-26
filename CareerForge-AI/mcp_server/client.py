import asyncio
import json
import os
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

ROOT = Path(__file__).resolve().parents[1]
SERVER_FILE = ROOT / "mcp_server" / "server.py"


def _decode_tool_result(result):
    if getattr(result, "isError", False):
        raise RuntimeError("MCP tool returned an error.")
    for item in getattr(result, "content", []):
        text = getattr(item, "text", None)
        if text:
            return json.loads(text)
    structured = getattr(result, "structuredContent", None)
    if structured is not None:
        return structured
    raise RuntimeError("MCP tool returned no readable content.")


async def _get_role_context(role: str, current_skills: list[str]) -> dict:
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER_FILE)],
        env=os.environ.copy(),
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            role_result = await session.call_tool("get_job_skills", {"role": role})
            role_data = _decode_tool_result(role_result)
            if "error" in role_data:
                raise ValueError(role_data["error"])

            required_skills = role_data["required_skills"]
            gap_result = await session.call_tool(
                "calculate_skill_gap",
                {
                    "current_skills": current_skills,
                    "required_skills": required_skills,
                },
            )
            skill_comparison = _decode_tool_result(gap_result)

            resources_result = await session.call_tool(
                "get_learning_resources",
                {"skills": skill_comparison["missing"]},
            )
            learning_resources = _decode_tool_result(resources_result)

    return {
        "required_skills": required_skills,
        "skill_comparison": skill_comparison,
        "learning_resources": learning_resources,
    }


def get_role_context(role: str, current_skills: list[str]) -> dict:
    """Synchronous bridge used by the LangGraph node to call the MCP server."""
    return asyncio.run(asyncio.wait_for(_get_role_context(role, current_skills), timeout=8.0))
