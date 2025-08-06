"""
Right Triangle Coordinate System

This module provides coordinate transformation functionality for right triangle plots.
"""

import numpy as np
from typing import Tuple, Union, List


class RightTriangleCoordinates:
    """
    Coordinate system for right triangle plots.
    
    This class handles the transformation between Cartesian coordinates and
    right triangle coordinate systems, where the triangle has vertices at
    (0,0), (1,0), and (0,1).
    """
    
    def __init__(self, orientation: str = "bottom-left"):
        """
        Initialize the coordinate system.
        
        Parameters:
        -----------
        orientation : str
            Orientation of the right angle. Options: 'bottom-left', 'bottom-right',
            'top-left', 'top-right'. Default is 'bottom-left'.
        """
        self.orientation = orientation
        self._validate_orientation()
    
    def _validate_orientation(self):
        """Validate the orientation parameter."""
        valid_orientations = ["bottom-left", "bottom-right", "top-left", "top-right"]
        if self.orientation not in valid_orientations:
            raise ValueError(f"Orientation must be one of {valid_orientations}")
    
    def to_cartesian(self, u: Union[float, np.ndarray], v: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert right triangle coordinates to Cartesian coordinates.
        
        Parameters:
        -----------
        u : float or array-like
            First coordinate (0 <= u <= 1)
        v : float or array-like  
            Second coordinate (0 <= v <= 1-u)
            
        Returns:
        --------
        x, y : tuple of arrays
            Cartesian coordinates
        """
        u = np.asarray(u)
        v = np.asarray(v)
        
        # Validate inputs
        if np.any(u < 0) or np.any(u > 1):
            raise ValueError("u coordinates must be between 0 and 1")
        if np.any(v < 0) or np.any(v > 1 - u):
            raise ValueError("v coordinates must be between 0 and 1-u")
        
        if self.orientation == "bottom-left":
            x = u
            y = v
        elif self.orientation == "bottom-right":
            x = 1 - u
            y = v
        elif self.orientation == "top-left":
            x = u
            y = 1 - v
        elif self.orientation == "top-right":
            x = 1 - u
            y = 1 - v
        
        return x, y
    
    def from_cartesian(self, x: Union[float, np.ndarray], y: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Convert Cartesian coordinates to right triangle coordinates.
        
        Parameters:
        -----------
        x, y : float or array-like
            Cartesian coordinates
            
        Returns:
        --------
        u, v : tuple of arrays
            Right triangle coordinates
        """
        x = np.asarray(x)
        y = np.asarray(y)
        
        if self.orientation == "bottom-left":
            u = x
            v = y
        elif self.orientation == "bottom-right":
            u = 1 - x
            v = y
        elif self.orientation == "top-left":
            u = x
            v = 1 - y
        elif self.orientation == "top-right":
            u = 1 - x
            v = 1 - y
        
        return u, v
    
    def get_triangle_vertices(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get the vertices of the right triangle in Cartesian coordinates.
        
        Returns:
        --------
        x_vertices, y_vertices : tuple of arrays
            Coordinates of triangle vertices
        """
        if self.orientation == "bottom-left":
            x_vertices = np.array([0, 1, 0, 0])
            y_vertices = np.array([0, 0, 1, 0])
        elif self.orientation == "bottom-right":
            x_vertices = np.array([1, 0, 1, 1])
            y_vertices = np.array([0, 0, 1, 0])
        elif self.orientation == "top-left":
            x_vertices = np.array([0, 1, 0, 0])
            y_vertices = np.array([1, 1, 0, 1])
        elif self.orientation == "top-right":
            x_vertices = np.array([1, 0, 1, 1])
            y_vertices = np.array([1, 1, 0, 1])
        
        return x_vertices, y_vertices
    
    def is_inside_triangle(self, u: Union[float, np.ndarray], v: Union[float, np.ndarray]) -> np.ndarray:
        """
        Check if points are inside the right triangle.
        
        Parameters:
        -----------
        u, v : float or array-like
            Right triangle coordinates
            
        Returns:
        --------
        inside : array of bool
            Boolean array indicating which points are inside the triangle
        """
        u = np.asarray(u)
        v = np.asarray(v)
        
        return (u >= 0) & (v >= 0) & (u + v <= 1)
    
    def generate_grid(self, n_points: int = 20) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate a regular grid of points in right triangle coordinates.
        
        Parameters:
        -----------
        n_points : int
            Number of grid points along each axis
            
        Returns:
        --------
        u_grid, v_grid : tuple of arrays
            Grid coordinates in right triangle space
        """
        u_vals = np.linspace(0, 1, n_points)
        u_grid = []
        v_grid = []
        
        for u in u_vals:
            v_max = 1 - u
            n_v = max(1, int(n_points * v_max))
            v_vals = np.linspace(0, v_max, n_v)
            u_grid.extend([u] * len(v_vals))
            v_grid.extend(v_vals)
        
        return np.array(u_grid), np.array(v_grid)
