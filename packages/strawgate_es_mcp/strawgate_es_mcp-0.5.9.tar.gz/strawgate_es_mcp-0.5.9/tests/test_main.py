from typing import Any

import pytest
from elasticsearch import AsyncElasticsearch
from fastmcp import FastMCP

from strawgate_es_mcp.main import build_es_client, build_server


@pytest.mark.asyncio
async def test_tags():
    es: AsyncElasticsearch = build_es_client(es_host="http://localhost:9200", api_key="")
    server: FastMCP[Any] = await build_server(es, include_tags=["esql"])

    assert server is not None

    assert server.include_tags == {"esql"}
    assert server.exclude_tags is None

    tools = await server._list_tools()
    tools_by_name = {tool.name: tool for tool in tools}

    assert len(tools) == 7
    assert "query" in tools_by_name
    assert "async_query" in tools_by_name
    assert "async_query_delete" in tools_by_name
    assert "async_query_get" in tools_by_name
    assert "async_query_stop" in tools_by_name
