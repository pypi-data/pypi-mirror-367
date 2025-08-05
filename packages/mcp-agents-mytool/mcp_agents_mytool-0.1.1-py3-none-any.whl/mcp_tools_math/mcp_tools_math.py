import numpy as np
import math
import json
import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def solve_quadratic(a, b, c):
    """
    solve_quadratic tool:
    The user gives equation in the form of ax**2 + bx + c. The tool should evaluate the 
    equation by using the a,b,c values of the equation.
    Example:
    2x**2 + 5x - 3 is the equation.
    Then a=2, b=5, c=-3.

    After getting the a,b,c values from the user query, get the roots of the equation.

    """
    discriminant = b**2 - 4*a*c
    
    if discriminant > 0:
        root1 = (-b + math.sqrt(discriminant)) / (2*a)
        root2 = (-b - math.sqrt(discriminant)) / (2*a)
        return f"Two Real Roots: {root1:.2f}, {root2:.2f}"
    
    elif discriminant == 0:
        root = -b / (2*a)
        return f"One Real Root: {root:.2f}"
    
    else:
        real_part = -b / (2*a)
        imag_part = math.sqrt(-discriminant) / (2*a)
        return f"Two Complex Roots: {real_part:.2f} + {imag_part:.2f}i and {real_part:.2f} - {imag_part:.2f}i"
    

@mcp.tool()
def matrix_multiply(A,B):
    """
    Matrix Multiplication tool:
    The user provides two matrices A and B in his query. 
    Then evaluate them and perform the matrix multiplication.

    """

    
    try:
        A_np = np.array(A)
        B_np = np.array(B)
        
        result = np.matmul(A_np, B_np)

        print(result)
    except:
        return "No proper order of matrix"

@mcp.tool()
def eigen_tool(matrix):
    """
    Eigen tool:
    The user will provide a matrix in his query. 
    Then evaluate the matrix and get the eigen values and eigen vectors. 
    """
     
    mat_np = np.array(matrix)
    eigenvalues, eigenvectors = np.linalg.eig(mat_np)

 
    print(eigenvalues)
    print(eigenvectors)
