from mcp.server.fastmcp import FastMCP
import numpy as np

mcp = FastMCP(name="MathTools")

@mcp.tool()
def matrix_multiplication(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    """Multiply two matrices."""
    try:
        result = np.matmul(np.array(a), np.array(b)).tolist()
        return result
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def quadratic_equation_solver(a: float, b: float, c: float) -> dict:
    """Solve quadratic equation ax^2 + bx + c = 0."""
    try:
        discriminant = b**2 - 4*a*c
        if discriminant > 0:
            root1 = (-b + discriminant**0.5) / (2*a)
            root2 = (-b - discriminant**0.5) / (2*a)
            return {"roots": [root1, root2], "type": "real and distinct"}
        elif discriminant == 0:
            root = -b / (2*a)
            return {"roots": [root], "type": "real and equal"}
        else:
            real_part = -b / (2*a)
            imaginary_part = (abs(discriminant)**0.5) / (2*a)
            return {
                "roots": [f"{real_part} + {imaginary_part}i", f"{real_part} - {imaginary_part}i"],
                "type": "complex"
            }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def eigen_solver(matrix: list[list[float]]) -> dict:
    """Find eigenvalues and eigenvectors of a matrix."""
    try:
        eigenvalues, eigenvectors = np.linalg.eig(np.array(matrix))
        return {
            "eigenvalues": eigenvalues.tolist(),
            "eigenvectors": eigenvectors.tolist()
        }
    except Exception as e:
        return {"error": str(e)}
