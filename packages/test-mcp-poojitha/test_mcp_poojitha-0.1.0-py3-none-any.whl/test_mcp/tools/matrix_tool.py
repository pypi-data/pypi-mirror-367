import numpy as np
from mcp import tool

@tool
def matrix_multiplication(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """
    Multiply two matrices A and B.
    """
    result = np.matmul(a, b).tolist()
    return result
