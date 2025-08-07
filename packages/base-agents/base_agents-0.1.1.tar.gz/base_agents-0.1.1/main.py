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
