"""
Basic Example: Simple Right Triangle Plot

This example demonstrates basic functionality of the extraction-triangle library.
"""

import numpy as np
import matplotlib.pyplot as plt
from extraction_triangle import RightTrianglePlot

def basic_scatter_example():
    """Create a basic scatter plot in right triangle coordinates."""
    # Generate sample data points
    np.random.seed(42)
    n_points = 50
    
    # Generate random points that satisfy triangle constraints
    u = np.random.random(n_points)
    v_max = 1 - u  # Maximum v for each u to stay within triangle
    v = np.random.random(n_points) * v_max
    
    # Create the plot
    rt_plot = RightTrianglePlot(orientation="bottom-left")
    
    # Add scatter plot
    rt_plot.scatter(u, v, c='blue', s=50, alpha=0.7, label='Data Points')
    
    # Add grid and labels
    rt_plot.add_grid(n_lines=10)
    rt_plot.add_labels("Component A", "Component B")
    rt_plot.set_title("Basic Right Triangle Scatter Plot")
    rt_plot.legend()
    
    # Show the plot
    rt_plot.show()

def extraction_curve_example():
    """Demonstrate plotting extraction curves."""
    # Create extraction curve data
    u_curve = np.linspace(0, 0.8, 100)
    v_curve = 0.9 - u_curve  # Simple linear relationship
    
    # Ensure points stay within triangle
    valid_points = (u_curve + v_curve) <= 1
    u_curve = u_curve[valid_points]
    v_curve = v_curve[valid_points]
    
    # Create plot
    rt_plot = RightTrianglePlot()
    
    # Plot extraction curve
    rt_plot.plot(u_curve, v_curve, color='red', linewidth=2, label='Extraction Curve')
    
    # Add some operating points
    u_points = [0.1, 0.3, 0.5, 0.7]
    v_points = [0.8, 0.6, 0.4, 0.2]
    rt_plot.scatter(u_points, v_points, c='green', s=100, marker='s', 
                   label='Operating Points')
    
    # Customize plot
    rt_plot.add_grid()
    rt_plot.add_labels("Extract Composition", "Raffinate Composition")
    rt_plot.set_title("Liquid-Liquid Extraction Process")
    rt_plot.legend()
    
    rt_plot.show()

def contour_example():
    """Demonstrate contour plotting."""
    # Generate grid data
    n_grid = 30
    u_vals = np.linspace(0, 1, n_grid)
    v_vals = np.linspace(0, 1, n_grid)
    
    # Create triangular grid
    u_grid = []
    v_grid = []
    z_values = []
    
    for u in u_vals:
        for v in v_vals:
            if u + v <= 1:  # Only points inside triangle
                u_grid.append(u)
                v_grid.append(v)
                # Example function: distance from origin
                z = np.sqrt(u**2 + v**2)
                z_values.append(z)
    
    u_grid = np.array(u_grid)
    v_grid = np.array(v_grid)
    z_values = np.array(z_values)
    
    # Create contour plot
    rt_plot = RightTrianglePlot()
    
    # Add filled contours
    contour_filled = rt_plot.contourf(u_grid, v_grid, z_values, levels=10, cmap='viridis', alpha=0.8)
    
    # Add contour lines
    contour_lines = rt_plot.contour(u_grid, v_grid, z_values, levels=10, colors='black', alpha=0.6)
    
    # Add colorbar
    rt_plot.add_colorbar(contour_filled, label='Value')
    
    # Customize plot
    rt_plot.add_labels("U Coordinate", "V Coordinate")
    rt_plot.set_title("Contour Plot Example")
    
    rt_plot.show()

if __name__ == "__main__":
    print("Running basic scatter example...")
    basic_scatter_example()
    
    print("Running extraction curve example...")
    extraction_curve_example()
    
    print("Running contour example...")
    contour_example()
