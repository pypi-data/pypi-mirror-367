"""
Script Name: utils.py
Author: Deniz
Created: 2024-08-26 18:16:23
Description: Script Description
"""

import numpy as np
from scipy.linalg import schur, eig

def visualize_eigenvectors(matrix, space=None):
    """
    Visualizes the eigenvectors of a matrix in a 3D space.

    Parameters:
    matrix (array-like): The matrix whose eigenvectors will be visualized.
    space (Space): Optional. The Space object where the eigenvectors will be visualized.
                   If not provided, a new Space will be created.
    """
    matrix = np.array(matrix)
    _, eigenvectors = eig(matrix)

    if space is None:
        space = Space()

    for vec in eigenvectors.T:
        space.add_vector(np.real(vec), color='blue')

    space.show()

def visualize_schur_decomposition(matrix, space=None):
    """
    Visualizes the Schur decomposition of a matrix in a 3D space.

    Parameters:
    matrix (array-like): The matrix to be decomposed and visualized.
    space (Space): Optional. The Space object where the matrix will be visualized.
                   If not provided, a new Space will be created.
    """
    matrix = np.array(matrix)
    Q, T = schur(matrix)

    if space is None:
        space = Space()

    # Visualize orthogonal matrix Q as vectors
    for vec in Q.T:
        space.add_vector(np.real(vec), color='green')

    # Visualize the upper triangular matrix T as a surface
    space.add_surface(z_data=T, color='red')

    space.show()

# Example usage of utility functions
if __name__ == "__main__":
    matrix = np.array([[1, 2], [3, 4]])

    # Visualize eigenvectors
    visualize_eigenvectors(matrix)

    # Visualize Schur decomposition
    visualize_schur_decomposition(matrix)
