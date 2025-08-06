import asyncio
from langchain.tools import StructuredTool
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import Tool


class AgentToolWrapper:
    def __init__(
        self,
        model,
        *,
        mcp_tools=None,
        simple_tools=None,
        sub_agent_tools=None,
        system_prompt=str,
    ):

        if not system_prompt or not isinstance(system_prompt, str):
            raise ValueError("system_prompt is required and must be a non-empty string")
        self.model = model
        self.mcp_tools = mcp_tools
        self.sub_agent_tools = sub_agent_tools
        self.system_prompt = system_prompt
        self.simple_tools = self._initialize_simple_tools(simple_tools)

    def _initialize_simple_tools(self, simple_tools):
        """Convert dictionary-style tools to Tool objects if needed"""
        if not simple_tools:
            return []

        converted_tools = []
        for tool in simple_tools:
            if isinstance(tool, dict):
                converted_tools.append(
                    Tool.from_function(
                        name=tool["name"],
                        func=tool["func"],
                        description=tool["description"],
                    )
                )
            elif isinstance(tool, Tool):
                converted_tools.append(tool)
            else:
                raise ValueError(f"Invalid tool format: {type(tool)}")

        return converted_tools

    async def run_agent(self, input_text: str) -> str:
        client_tools = []

        if self.mcp_tools is not None:
            client = MultiServerMCPClient(self.mcp_tools)
            client_tools = await client.get_tools() if self.mcp_tools else []

        all_tools = (
            (client_tools or [])
            + (self.simple_tools or [])
            + (self.sub_agent_tools or [])
        )

        agent = create_react_agent(self.model, all_tools)

        response = await agent.ainvoke(
            {
                "messages": [
                    SystemMessage(content=self.system_prompt),
                    HumanMessage(content=input_text),
                ]
            }
        )

        # Return the last message content
        return response["messages"][-1].content

    def run_agent_sync(self, input_text: str) -> str:
        return asyncio.run(self.run_agent(input_text))


def create_agent_tool(
    model,
    mcp_tools=None,
    simple_tools=None,
    sub_agent_tools=None,
    system_prompt=None,
) -> StructuredTool:
    wrapper = AgentToolWrapper(
        model,
        mcp_tools=mcp_tools,
        simple_tools=simple_tools,
        sub_agent_tools=sub_agent_tools,
        system_prompt=system_prompt,
    )

    return StructuredTool.from_function(
        name="Agent",
        description="You have access to tools and sub-agents",
        func=wrapper.run_agent_sync,
        coroutine=wrapper.run_agent,
    )
