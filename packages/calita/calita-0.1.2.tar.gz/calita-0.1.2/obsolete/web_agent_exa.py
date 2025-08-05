import asyncio
import json
import logging
from typing import Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

from calita.utils.mcp_config_loader import load_mcp_servers_config


class WebAgent:
    def __init__(self) -> None:
        mcp_servers_config: Dict[str, Any] = load_mcp_servers_config("mcp_config/mcp_web_agent_server.json")
        logging.info("Loaded MCP servers: %s", list(mcp_servers_config.keys()))
        self.mcp_client = MultiServerMCPClient(mcp_servers_config.get("mcpServers", {}))


    def _extract_search_result(self, search_response)->Dict[str, Any]:
        result = {}
        try:
            _response = json.loads(search_response)
            if 'results' in _response  and  len(_response['results']) > 1:
                content = _response['results']
                short_content = content[:1000] if len(content) >= 1000 else content
                result = {"result": short_content}
            else:
                result = {'error': "search result is empty"}
        except json.JSONDecodeError:
            result = {'error': "search result is not valid JSON"}
        return result

    async def _exa_search(self, query)-> Dict[str, Any]:
        result = {}
        try:
            logging.info(f"WebAgent<_exa_search>: query={query}")

            async with self.mcp_client.session("exa") as session:
                tools = await load_mcp_tools(session)
                web_search_tool = next(t for t in tools if t.name == "web_search_exa")
                response = await web_search_tool.arun({"query": query, "numResults": 3})
                result = self._extract_search_result(response)
        except Exception as e:
            logging.error("Exception occurred during Exa MCP search for query '%s': %s", query, str(e))
            result['error'] = str(e)

        return result

    def search(self, query: str) -> Dict[str, Any]:
        return asyncio.run(self.async_search(query))

    async def async_search(self, query: str) -> Dict[str, Any]:
        return await self._exa_search(query)

if __name__ == "__main__":
    from calita.utils.utils import get_global_config
    from calita.utils.utils import setup_logging

    config = get_global_config("config.yaml")
    setup_logging(config)

    web_agent = WebAgent()
    result = web_agent.search("北京本周的天气")
    print(result)