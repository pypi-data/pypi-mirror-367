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
    limit: Annotated[
        int, "The maximum number of results to return (default to 7 days)."
    ] = 7,
    project_ids: Annotated[
        Optional[list[str]], "The project IDs to filter by (optional)."
    ] = None,
) -> list[dict]:
    """Fetches the costs for the current month."""
    base_url = "https://api.openai.com/v1/organization/costs"
    params = {
        "start_time": int(start_time.timestamp()),
    }
    if end_time:
        params["end_time"] = int(end_time.timestamp())
    if group_by:
        params["group_by"] = group_by
    if limit:
        params["limit"] = limit
    if project_ids:
        params["project_ids"] = project_ids
    url = f"{base_url}?{urlencode(params)}"
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
                params["page"] = next_page
                url = f"{base_url}?{urlencode(params)}"
    return results


def main() -> None:
    """Run the OpenAI MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
