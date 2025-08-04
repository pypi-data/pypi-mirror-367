import math
from mcp import tool

@tool
def solve_quadratic(a: float, b: float, c: float) -> dict:
    """
    Solve a quadratic equation ax² + bx + c = 0.
    Returns real or complex roots.
    """
    discriminant = b**2 - 4*a*c

    if discriminant >= 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
    else:
        real = -b / (2*a)
        imag = math.sqrt(-discriminant) / (2*a)
        root1 = f"{real}+{imag}i"
        root2 = f"{real}-{imag}i"

    return {"root1": root1, "root2": root2}
