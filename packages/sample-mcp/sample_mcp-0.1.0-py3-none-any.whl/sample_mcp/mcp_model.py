from mcp.server.fastmcp import FastMCP
import numpy as np
import sympy as sp

mcp = FastMCP(name="MathTools")


@mcp.tool()
def matrix_multiply(a: list[list[float]], b: list[list[float]]) -> dict:
    """Multiply two matrices using both NumPy and SymPy."""
    try:
        # NumPy result
        np_result = np.matmul(np.array(a), np.array(b)).tolist()

        # SymPy result
        sp_result = (sp.Matrix(a) * sp.Matrix(b)).tolist()

        return {
            "numpy_result": np_result,
            "sympy_result": sp_result
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def solve_quadratic(a: float, b: float, c: float) -> dict:
    """Solve quadratic equation ax^2 + bx + c = 0 using NumPy and SymPy."""
    try:
        # NumPy-style float roots
        discriminant = b**2 - 4*a*c
        if discriminant > 0:
            r1 = (-b + np.sqrt(discriminant)) / (2*a)
            r2 = (-b - np.sqrt(discriminant)) / (2*a)
            numeric_roots = [r1, r2]
            root_type = "real and distinct"
        elif discriminant == 0:
            r = -b / (2*a)
            numeric_roots = [r]
            root_type = "real and equal"
        else:
            real = -b / (2*a)
            imag = np.sqrt(-discriminant) / (2*a)
            numeric_roots = [f"{real}+{imag}i", f"{real}-{imag}i"]
            root_type = "complex"

        # SymPy exact roots
        x = sp.symbols('x')
        symbolic_roots = [str(root) for root in sp.solve(a * x**2 + b * x + c, x)]

        return {
            "numeric_roots": numeric_roots,
            "symbolic_roots": symbolic_roots,
            "type": root_type
        }

    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def eigen_solver(matrix: list[list[float]]) -> dict:
    """Compute eigenvalues and eigenvectors using NumPy and SymPy."""
    try:
        # NumPy eigenvalues & eigenvectors
        np_vals, np_vecs = np.linalg.eig(np.array(matrix))

        # SymPy eigenvalues and eigenvectors
        sp_matrix = sp.Matrix(matrix)
        eig_data = sp_matrix.eigenvects()
        symbolic = []
        for val, mult, vects in eig_data:
            symbolic.append({
                "eigenvalue": str(val),
                "multiplicity": mult,
                "eigenvectors": [str(v) for v in vects]
            })

        return {
            "numpy": {
                "eigenvalues": np_vals.tolist(),
                "eigenvectors": np_vecs.tolist()
            },
            "sympy": {
                "eigenpairs": symbolic
            }
        }

    except Exception as e:
        return {"error": str(e)}