import numpy as np
from mcp import tool

@tool
def solve_eigen(matrix: list[list[float]]) -> dict:
    """
    Compute eigenvalues and eigenvectors of a square matrix.
    """
    arr = np.array(matrix)
    values, vectors = np.linalg.eig(arr)
    return {
        "eigenvalues": values.tolist(),
        "eigenvectors": vectors.tolist()
    }
