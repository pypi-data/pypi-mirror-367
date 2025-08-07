# Base Agents

A simple way to build AI agents with tools, MCP (Model Context Protocol) tools, and sub-agents

## Features

- **Multiple Tool Types**: Support for simple functions, MCP (Model Context Protocol) tools, and sub-agents
- **Hierarchical Agent Architecture**: Create agents that can use other agents as tools
- **Async & Sync Support**: Both asynchronous and synchronous execution modes
- **Easy Integration**: Simple API that works with any LangChain-compatible model
- **Flexible Tool System**: Mix and match different types of tools in a single agent

## Installation

```bash
pip install base-agents
```

## Quick Start

### Basic Usage

```python
from base_agents import create_agent_tool
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
import numpy as np

load_dotenv()

model = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))


@tool
def complex_matrix_multiplication(
    matrix1: list[list[complex]], matrix2: list[list[complex]]
) -> list[list[complex]]:
    """
    Multiply two complex-valued matrices.

    Args:
        matrix1: First complex matrix as a 2D list (e.g., [[1+2j, 3+4j], [5+6j, 7+8j]])
        matrix2: Second complex matrix as a 2D list (same format as matrix1)

    Returns:
        The product of the two matrices as a 2D list of complex numbers

    Raises:
        ValueError: If matrices cannot be multiplied due to incompatible dimensions
    """
    np_matrix1 = np.array(matrix1, dtype=complex)
    np_matrix2 = np.array(matrix2, dtype=complex)

    try:
        result = np.matmul(np_matrix1, np_matrix2)
        return result.tolist()
    except ValueError as e:
        raise ValueError(f"Matrix multiplication error: {str(e)}")


simple_tools = [complex_matrix_multiplication]

# mcp_tools = {
#     "puppeteer": {
#         "command": "npx",
#         "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
#         "transport": "stdio",
#     }
# }

# sub_agent_math = [
#     create_agent_tool(
#         model,
#         simple_tools=simple_tools,
#         system_prompt="You are a subagent that can perform large number calculations.",
#     )
# ]

# Create Main Agent
agent = create_agent_tool(
    model,
    simple_tools=simple_tools,
    # mcp_tools=mcp_tools,
    # sub_agent_tools=sub_agent_math,
    system_prompt="You are a helpful assistant that can use tools and sub-agents to search online.",
)

# Example usage
response = agent.invoke(
    "Multiply the following two complex-valued matrices and return the result: Matrix A: [[1+2j, 3+4j], [5+6j, 7+8j]] Matrix B: [[2+1j, 0+3j], [1+2j, 4+0j]]"
)
print("Response:", response)
```

## API Reference

### `create_agent_tool()`

Creates a structured tool that wraps an agent with various capabilities.

**Parameters:**

**Args:**

- **model**: A LangChain-compatible chat model _(required)_
- **mcp_tools**: Dictionary defining MCP (Model Context Protocol) tools _(optional)_
- **simple_tools**: List of simple function tools _(optional)_
- **sub_agent_tools**: List of other agent tools _(optional)_
- **system_prompt**: System prompt for the agent _(required)_

**Raises:**

- **ValueError**: If all tools (`mcp_tools`, `simple_tools`, and `sub_agent_tools`) are `None`. At least one tool type must be provided.

**Returns:**

A `StructuredTool` that can be used with LangChain's agent frameworks.

### Tool Types

#### Simple Tools

To write simple tools, use the `@tool` decorator from `langchain_core.tools` on a function, specifying input types and a docstring. The function should perform a specific task and return a result.

```python
from langchain_core.tools import tool

@tool
def math_tool(x: float, y: float) -> float:
    """Add two numbers together"""
    return x + y


simple_tools = [math_tool]
```

#### MCP Tools

MCP tools enable integration with external services:

```python
mcp_tools = {
    "puppeteer": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {"PUPPETEER_LAUNCH_OPTIONS": '{ "headless": true }'},
        "transport": "stdio",
    },
}
```

#### Sub-agent Tools

Sub-agent tools are other agents created with `create_agent_tool()`:

```python
math_agent = create_agent_tool(model, simple_tools=math_tools)
main_agent = create_agent_tool(model, sub_agent_tools=[math_agent])
```

## Usage Patterns

### Synchronous Execution

```python
response = agent.invoke("Your question here")
```

### Asynchronous Execution

```python
response = await agent.ainvoke("Your question here")
```

### Concurrent Execution

```python
import asyncio

async def run_multiple_tasks():
    tasks = [
        agent.ainvoke("Question 1"),
        agent.ainvoke("Question 2"),
        agent.ainvoke("Question 3"),
    ]
    responses = await asyncio.gather(*tasks)
    return responses
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
