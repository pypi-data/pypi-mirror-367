from mcp.server.fastmcp import FastMCP
from sympy import symbols, Eq, solve, Matrix
from typing import List

mcp = FastMCP(name="MathTools")

@mcp.tool()
def quadratic_solver(a: float, b: float, c: float) -> str:
    """Solves quadratic equations ax^2 + bx + c = 0"""
    x = symbols('x')
    equation = Eq(a * x**2 + b * x + c, 0)
    roots = solve(equation, x)
    return f"Solutions for {a}x² + {b}x + {c} = 0: {roots}"

@mcp.tool()
def eigen_solver(matrix_values: List[List[float]]) -> str:
    """Computes eigenvalues and eigenvectors of a square matrix"""
    mat = Matrix(matrix_values)
    eigen_data = mat.eigenvects()
    return "\n".join(
        f"Eigenvalue: {val}, Multiplicity: {mult}, Eigenvector(s): {vec}"
        for val, mult, vec in eigen_data
    )

@mcp.tool()
def matrix_multiplier(matrix_a: List[List[float]], matrix_b: List[List[float]]) -> str:
    """Multiplies two matrices A × B"""
    result = Matrix(matrix_a) * Matrix(matrix_b)
    return f"Matrix multiplication result:\n{result}"

if __name__ == "__main__":
    mcp.serve()
