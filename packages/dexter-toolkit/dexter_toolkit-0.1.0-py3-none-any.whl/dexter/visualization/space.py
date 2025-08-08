"""
Script Name: space.py
Author: Deniz
Created: 2024-08-26 18:17:34
Description: Space structure for multidimensional-array visualizations
"""

import plotly.graph_objs as go
import numpy as np

class Space:
    def __init__(self, x_size=10, y_size=10, z_size=10, grid_density=10):
        """
        Initializes and automatically displays an empty 3D space using Plotly.

        Parameters:
        x_size (int): The size of the space along the x-axis (default is 10).
        y_size (int): The size of the space along the y-axis (default is 10).
        z_size (int): The size of the space along the z-axis (default is 10).
        """
        self.x_size = x_size
        self.y_size = y_size
        self.z_size = z_size
        self.grid_density = grid_density
        self.fig = go.Figure()

        self._create_space()

    def _create_space(self):
        """
        Creates the 3D space with the given dimensions.
        """
        self.fig.update_layout(
            scene=dict(
                xaxis=dict(nticks=10, range=[-self.x_size, self.x_size]),
                yaxis=dict(nticks=10, range=[-self.y_size, self.y_size]),
                zaxis=dict(nticks=10, range=[-self.z_size, self.z_size]),
            ),
            width=700,
            margin=dict(r=20, l=10, b=10, t=10)
        )

    def add_vector(self, vector, color='red'):
        """
        Adds a vector to the 3D space.

        Parameters:
        vector (array-like): A 3D vector represented as a list or numpy array.
        color (str): The color of the vector (default is 'red').
        """
        vector = np.array(vector)
        origin = np.array([0, 0, 0])
        
        self.fig.add_trace(go.Scatter3d(
            x=[origin[0], vector[0]],
            y=[origin[1], vector[1]],
            z=[origin[2], vector[2]],
            marker=dict(size=4),
            line=dict(color=color, width=5)
        ))

    def add_surface(self, z_data, x_data=None, y_data=None):
        """
        Adds a surface plot to the 3D space.

        Parameters:
        z_data (array-like): The z-values of the surface.
        x_data (array-like): Optional. The x-values corresponding to z_data.
        y_data (array-like): Optional. The y-values corresponding to z_data.
        color (str): The color of the surface (default is 'blue').
        """
        if x_data is None or y_data is None:
            x_data, y_data = np.meshgrid(range(z_data.shape[0]), range(z_data.shape[1]))

        self.fig.add_trace(go.Surface(z=z_data, x=x_data, y=y_data))

    def add_mesh_grid(self):
        """
        Adds a mesh grid to the 3D space, automatically adjusted to the size of the space.
        """
        x_points = np.linspace(-self.x_size, self.x_size, self.grid_density)
        y_points = np.linspace(-self.y_size, self.y_size, self.grid_density)
        z_points = np.linspace(-self.z_size, self.z_size, self.grid_density)

        for x in x_points:
            for y in y_points:
                for z in z_points:
                    self.fig.add_trace(go.Scatter3d(
                        x=[x], y=[y], z=[z],
                        mode='markers',
                        marker=dict(size=3, color='gray')
                    ))

    def show(self):
        """
        Displays the 3D space.
        """
        self.fig.show()

# Example of using the enhanced Space class
if __name__ == "__main__":
    space = Space(x_size=15, y_size=15, z_size=15)

    # Add a vector
    space.add_vector([10, 10, 10], color='green')

    # Add a surface
    z = np.array([[1, 2, 3], [2, 3, 4], [3, 4, 5]])
    space.add_surface(z_data=z)

    space.show()
