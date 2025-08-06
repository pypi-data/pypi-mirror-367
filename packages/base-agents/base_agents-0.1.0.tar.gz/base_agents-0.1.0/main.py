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