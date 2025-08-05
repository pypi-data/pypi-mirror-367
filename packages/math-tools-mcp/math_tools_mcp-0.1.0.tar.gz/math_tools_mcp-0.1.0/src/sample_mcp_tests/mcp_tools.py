from mcp.server.fastmcp import FastMCP
from sympy import symbols, solve, sympify, Poly, N
import numpy as np
import json

mcp = FastMCP()

@mcp.tool()
async def quadratic_tool_handler(tool_context, args: dict) -> str:
    """
    Solves the quadratic equation ax^2 + bx + c = 0.

    :param a: Coefficient of x^2
    :param b: Coefficient of x
    :param c: Constant term
    :return: The roots of the equation.
    
    """

    if isinstance(args, str):
        args = json.loads(args)

    a = args.get("a")
    b = args.get("b")
    c = args.get("c")

    x = symbols('x')
    try:
        if a == 0:
            return "Error: 'a' must not be zero in a quadratic equation."

        expr = a * x**2 + b * x + c
        roots = [N(r, 5) for r in solve(expr, x)]
        return f"Equation: {a}*x^2 + {b}*x + {c} = 0\nRoots: {roots}"
    except Exception as e:
        return f"Error: {str(e)}"
    


@mcp.tool()
def eigen_solver(matrix_input: str) -> str:
    """
    Solves for eigenvalues and eigenvectors of a square matrix.
    :args:
    matrix_input: The provided matrix that is used to obtain eigen values and vectors \
        Input format: expects a square matrix i.e '[ [a11, a12], [a21, a22] ]' as a string \
        Example: '[[2, -1], [1, 4]]'
    
    :returns: 
    A string containing the input matrix, its eigenvalues, and eigenvectors.

    """

    try:
        matrix = eval(matrix_input, {"__builtins__": {}})

        np_matrix = np.array(matrix)

        if np_matrix.shape[0] != np_matrix.shape[1]:
            return "Error: Matrix must be square."

        eigenvalues, eigenvectors = np.linalg.eig(np_matrix)

        # Format output
        eigenvalues = [round(val, 5) for val in eigenvalues]
        eigenvectors = [[round(val, 5) for val in vec] for vec in eigenvectors.T]

        return (
            f"Input Matrix:\n{np_matrix}\n\n"
            f"Eigenvalues:\n{eigenvalues}\n\n"
            f"Eigenvectors (columns):\n{eigenvectors}"
        )

    except Exception as e:
        return f"Error: {str(e)}"
    

@mcp.tool()
def matrix_multiplication_solver(A: list[list[float]], B: list[list[float]]) -> str:
    """
    Multiplies two matrices using NumPy.

    :args:
    :param A: First matrix as a list of lists
    :param B: Second matrix as a list of lists
    :return: Matrix product as string or error message
    """
    try:
        A_np = np.array(A)
        B_np = np.array(B)

        # Check matrix shape compatibility
        if A_np.shape[1] != B_np.shape[0]:
            return f"Error: Incompatible shapes for multiplication: {A_np.shape} x {B_np.shape}"

        result = np.matmul(A_np, B_np)

        return (
            f"Matrix A:\n{A_np}\n\n"
            f"Matrix B:\n{B_np}\n\n"
            f"Result (A x B):\n{result}"
        )

    except Exception as e:
        return f"Error: {str(e)}"