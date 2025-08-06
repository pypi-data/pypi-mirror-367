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
from langchain_mistralai import ChatMistralAI

load_dotenv()

model = ChatMistralAI(
    model="mistral-large-latest",
    api_key=os.getenv("MISTRAL_API_KEY")
)

# Simple MCP tools configuration
mcp_tools = {
    "web_scraper": {
        "command": "npx",
        "args": ["@modelcontextprotocol/server-puppeteer"],
        "transport": "stdio",
    },
}

# Create agent with MCP tools
agent = create_agent_tool(
    model,
    mcp_tools=mcp_tools,
    system_prompt="You can browse the web using tools.",
)

# Synchronous example
response = agent.invoke("Use the web scraper to get the title of example.com")
print("Response:", response)
```

### Advanced Usage
```python
from base_agents import create_agent_tool
import os
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

load_dotenv()

model = ChatMistralAI(
    model="mistral-large-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
    verbose=True
)

simple_tools = [
    {
        "name": "Difficult_Addition",
        "func": lambda x, y: x + y,
        "description": "Add two large numbers together",
    },
    {
        "name": "Complex_Multiplication",
        "func": lambda x, y: x * y,
        "description": "Multiply two large numbers together",
    },
]

mcp_tools = {
    "puppeteer": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-puppeteer"],
        "env": {
            "PUPPETEER_LAUNCH_OPTIONS": '{ "headless": true}',
        },
        "transport": "stdio",
    },
}

sub_agent_math = [
    create_agent_tool(
        model,
        simple_tools=simple_tools,
        system_prompt="You are a subagent that can perform large number calculations.",
    )
]


agent = create_agent_tool(
    model,
    sub_agent_tools=sub_agent_math,
    system_prompt="You are a helpful assistant that can use tools and sub-agents to answer questions.",
)

# Example 1: Synchronous invocation
def example_sync():
    """Example of synchronous agent invocation"""
    print("\n--- Synchronous Example ---")
    response = agent.invoke("What's is 123456789 + 987654321? Use available agents")
    print("Question:", "What's is 123456789 + 987654321? Use available agents")
    print("Response:", response)

# Example 2: Asynchronous invocation
async def example_async():
    """Example of asynchronous agent invocation"""
    print("\n--- Asynchronous Example ---")
   
    task1 = agent.ainvoke("What is the capital of France?")
    task2 = agent.ainvoke("What is 2 + 2?")
    
    responses = await asyncio.gather(task1, task2)
    
    for i, response in enumerate(responses, 1):
        print(f"Question {i}:", response['input'])
        print(f"Response {i}:", response['output'])

if __name__ == "__main__":
    import asyncio
    
    # Run synchronous example
    example_sync()
    
    # Run asynchronous example
    print("\nRunning async examples...")
    asyncio.run(example_async())
```

## API Reference

### `create_agent_tool()`

Creates a structured tool that wraps an agent with various capabilities.

**Parameters:**

**Args:**
- **model**: A LangChain-compatible chat model *(required)*  
- **mcp_tools**: Dictionary defining MCP (Model Context Protocol) tools *(optional)*  
- **simple_tools**: List of simple function tools *(optional)*  
- **sub_agent_tools**: List of other agent tools *(optional)*  
- **system_prompt**: System prompt for the agent *(required)*  

**Raises:**
- **ValueError**: If all tools (`mcp_tools`, `simple_tools`, and `sub_agent_tools`) are `None`. At least one tool type must be provided.

**Returns:**

A `StructuredTool` that can be used with LangChain's agent frameworks.

### Tool Types

#### Simple Tools
Simple tools are defined as dictionaries with:
- `name`: Tool name
- `func`: The function to execute
- `description`: Tool description

```python
simple_tools = [
    {
        "name": "calculator",
        "func": lambda x, y: x + y,
        "description": "Add two numbers",
    }
]
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
