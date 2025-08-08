import numpy as np
import plotly.graph_objs as go
from scipy.linalg import schur, eig

"""
Script Name: matrix.py
Author: Deniz
Created: 2024-08-26 18:01:57
Description: Script Description
"""


class Matrix3D:
    def __init__(self, matrix):
        """
        Initializes a Matrix3D object.

        Parameters:
        matrix (array-like): The matrix to be encapsulated by this class.
        """
        self.matrix = np.array(matrix)

    def schur_decomposition(self):
        """
        Computes the Schur decomposition of the matrix.
        
        Returns:
        Q (ndarray): The orthogonal matrix.
        T (ndarray): The upper triangular matrix.
        """
        Q, T = schur(self.matrix)
        return Q, T

    def eigen_decomposition(self):
        """
        Computes the eigenvalue decomposition of the matrix.
        
        Returns:
        w (ndarray): The eigenvalues of the matrix.
        v (ndarray): The eigenvectors of the matrix.
        """
        w, v = eig(self.matrix)
        return w, v

    def visualize_matrix(self, space):
        """
        Visualizes the matrix as a 3D surface plot in the given space.

        Parameters:
        space (Space): The Space object where the matrix will be visualized.
        """
        # For simplicity, assume the matrix represents a 2D grid that can be plotted in 3D
        x, y = np.meshgrid(range(self.matrix.shape[0]), range(self.matrix.shape[1]))
        z = self.matrix
        
        surface = go.Surface(z=z, x=x, y=y)
        space.fig.add_trace(surface)
        space.show()

# Example usage
if __name__ == "__main__":
    # Create a matrix
    matrix = [[1, 2], [3, 4]]

    # Initialize the Matrix3D object
    mat3d = Matrix3D(matrix)

    # Perform Schur decomposition
    Q, T = mat3d.schur_decomposition()
    print("Schur Decomposition:")
    print("Q =", Q)
    print("T =", T)

    # Create a 3D space and visualize the matrix
    space = Space()
    mat3d.visualize_matrix(space)
