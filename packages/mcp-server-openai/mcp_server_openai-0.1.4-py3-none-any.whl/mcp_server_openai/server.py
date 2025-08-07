import asyncio
import os
from urllib.parse import urlencode
from fastmcp import FastMCP
import httpx
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Annotated, Literal, Optional

OPENAI_ADMIN_API_KEY = os.getenv("OPENAI_ADMIN_API_KEY")


mcp = FastMCP(
    name="OpenAI MCP Server",
    instructions="A Model Context Protocol server that provides tools to manage OpenAI API keys, spending, and usage via the Admin API.",
)


@mcp.tool(description="Fetches OpenAI costs for the specified period.")
async def get_costs(
    start_time: Annotated[datetime, "The start time as a UTC timestamp."],
    end_time: Annotated[
        Optional[datetime], "The end time as a UTC timestamp (defaults to now)."
    ] = None,
    group_by: Annotated[
        Optional[list[Literal["project_id", "line_item"]]],
        "The fields to group by (optional). Group the costs by the specified fields. Support fields include project_id, line_item and any combination of them.",
    ] = None,
    project_ids: Annotated[
        Optional[list[str]], "The project IDs to filter by (optional)."
    ] = None,
) -> list[dict]:
    """Fetches the costs for the current month."""

    base_url = "https://api.openai.com/v1/organization/costs"
    params: list[tuple[str, str]] = [
        ("start_time", int(start_time.timestamp())),
        ("limit", 180),
    ]
    if end_time:
        params.append(("end_time", int(end_time.timestamp())))

    if group_by:
        for field in group_by:
            params.append(("group_by", field))
    if project_ids:
        for project_id in project_ids:
            params.append(("project_ids", project_id))
    base_params = params.copy()
    url = f"{base_url}?{urlencode(base_params)}"
    results: list[dict] = []
    async with httpx.AsyncClient(
        timeout=60,
        headers={"Authorization": f"Bearer {OPENAI_ADMIN_API_KEY}"},
    ) as client:
        while url:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            items = data["data"]
            for item in items:
                item["start_time"] = datetime.fromtimestamp(item["start_time"])
                item["end_time"] = datetime.fromtimestamp(item["end_time"])
                results.append(item)
            next_page = data.get("next_page")
            has_more = data.get("has_more")
            url = None
            if next_page and has_more:
                params = base_params.copy()
                params.append(("page", next_page))
                url = f"{base_url}?{urlencode(params)}"
                # sleep to avoid rate limiting
                await asyncio.sleep(1.0)
    return results


@mcp.tool(description="Fetches OpenAI projects for the current organization.")
async def get_projects(
    include_archived: Annotated[
        bool, "Whether to include archived projects. Defaults to False."
    ] = False,
) -> list[dict]:
    """Fetches the projects for the current organization."""

    base_url = "https://api.openai.com/v1/organization/projects"
    params: list[tuple[str, str]] = [
        ("include_archived", include_archived),
        ("limit", 180),
    ]
    base_params = params.copy()
    url = f"{base_url}?{urlencode(base_params)}"
    results: list[dict] = []
    async with httpx.AsyncClient(
        timeout=60,
        headers={"Authorization": f"Bearer {OPENAI_ADMIN_API_KEY}"},
    ) as client:
        while url:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            items = data["data"]
            for item in items:
                item["created_at"] = datetime.fromtimestamp(item["created_at"])
                if "archived_at" in item and item["archived_at"]:
                    item["archived_at"] = datetime.fromtimestamp(item["archived_at"])
                results.append(item)
            last_id = data.get("last_id")
            has_more = data.get("has_more")
            url = None
            if last_id and has_more:
                params = base_params.copy()
                params.append(("after", last_id))
                url = f"{base_url}?{urlencode(params)}"
                # sleep to avoid rate limiting
                await asyncio.sleep(1.0)
    return results


def main() -> None:
    """Run the OpenAI MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
