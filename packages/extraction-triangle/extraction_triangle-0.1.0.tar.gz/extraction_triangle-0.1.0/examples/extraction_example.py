"""
Liquid-Liquid Extraction Example

This example demonstrates how to use the library for visualizing
liquid-liquid extraction processes.
"""

import numpy as np
import matplotlib.pyplot as plt
from extraction_triangle import RightTrianglePlot, RightTriangleCoordinates
from extraction_triangle.utils import generate_extraction_curve


def lle_equilibrium_example():
    """Demonstrate liquid-liquid equilibrium visualization."""
    
    # Equilibrium data for a hypothetical system
    # (Component A in extract phase, Component A in raffinate phase)
    x_extract = np.array([0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85])
    x_raffinate = np.array([0.90, 0.80, 0.70, 0.60, 0.50, 0.40, 0.30, 0.20, 0.10])
    
    # Convert to triangle coordinates
    # For a two-component system: u = x_A, v = x_B = 1 - x_A
    u_extract = x_extract
    v_extract = 1 - x_extract
    
    u_raffinate = x_raffinate  
    v_raffinate = 1 - x_raffinate
    
    # Create the plot
    rt_plot = RightTrianglePlot()
    
    # Plot equilibrium curve
    rt_plot.plot(u_extract, v_extract, color='blue', linewidth=2, 
                marker='o', markersize=6, label='Extract Phase')
    rt_plot.plot(u_raffinate, v_raffinate, color='red', linewidth=2,
                marker='s', markersize=6, label='Raffinate Phase')
    
    # Connect equilibrium points with tie lines
    for i in range(len(x_extract)):
        u_tie = [u_extract[i], u_raffinate[i]]
        v_tie = [v_extract[i], v_raffinate[i]]
        rt_plot.plot(u_tie, v_tie, color='gray', linewidth=1, alpha=0.6)
    
    # Add feed point
    u_feed = 0.4
    v_feed = 0.6
    rt_plot.scatter([u_feed], [v_feed], c='green', s=150, marker='*', 
                   label='Feed', edgecolors='black', linewidth=2)
    
    # Customize plot
    rt_plot.add_grid(n_lines=10)
    rt_plot.add_labels("Component A Fraction", "Component B Fraction")
    rt_plot.set_title("Liquid-Liquid Equilibrium Diagram")
    rt_plot.legend()
    
    return rt_plot


def extraction_stages_example():
    """Demonstrate multi-stage extraction visualization."""
    
    # Operating line data for counter-current extraction
    u_operating = np.linspace(0.1, 0.8, 10)
    v_operating = 0.9 - u_operating
    
    # Equilibrium curve (simplified)
    u_eq = np.linspace(0.05, 0.85, 20)
    v_eq = 0.95 - 1.2 * u_eq
    v_eq = np.clip(v_eq, 0, 1 - u_eq)  # Ensure valid triangle coordinates
    
    # Create plot
    rt_plot = RightTrianglePlot()
    
    # Plot operating line
    rt_plot.plot(u_operating, v_operating, color='blue', linewidth=2, 
                label='Operating Line')
    
    # Plot equilibrium curve
    rt_plot.plot(u_eq, v_eq, color='red', linewidth=2, 
                label='Equilibrium Curve')
    
    # Add stage construction (McCabe-Thiele style)
    n_stages = 5
    u_stages = np.linspace(0.15, 0.75, n_stages)
    
    for i, u in enumerate(u_stages):
        # Vertical line to equilibrium curve
        v_op = 0.9 - u  # From operating line
        
        # Find intersection with equilibrium curve (simplified)
        v_eq_point = 0.95 - 1.2 * u
        v_eq_point = max(0, min(v_eq_point, 1 - u))
        
        # Draw stage lines
        rt_plot.plot([u, u], [v_op, v_eq_point], 'k--', alpha=0.7, linewidth=1)
        rt_plot.plot([u, u], [v_eq_point, v_op], 'k--', alpha=0.7, linewidth=1)
        
        # Mark stage
        rt_plot.scatter([u], [v_op], c='black', s=30, marker='o')
        
    # Customize plot
    rt_plot.add_grid()
    rt_plot.add_labels("Solute in Extract", "Solvent in Extract")
    rt_plot.set_title("Multi-Stage Counter-Current Extraction")
    rt_plot.legend()
    
    return rt_plot


def phase_diagram_example():
    """Create a comprehensive phase diagram."""
    
    # Create multiple orientation plots
    orientations = ["bottom-left", "bottom-right", "top-left", "top-right"]
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 12))
    axes = axes.flatten()
    
    for i, orientation in enumerate(orientations):
        # Create coordinate system
        coords = RightTriangleCoordinates(orientation)
        
        # Generate sample data
        np.random.seed(42)
        n_points = 30
        u = np.random.random(n_points)
        v_max = 1 - u
        v = np.random.random(n_points) * v_max
        
        # Convert to Cartesian for plotting
        x, y = coords.to_cartesian(u, v)
        
        # Plot on subplot
        ax = axes[i]
        ax.scatter(x, y, c='blue', s=30, alpha=0.7)
        
        # Draw triangle boundary
        x_verts, y_verts = coords.get_triangle_vertices()
        ax.plot(x_verts, y_verts, 'k-', linewidth=2)
        
        # Customize subplot
        ax.set_aspect('equal')
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
        ax.set_title(f"Orientation: {orientation}")
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.suptitle("Right Triangle Plots with Different Orientations", y=1.02)
    plt.show()


if __name__ == "__main__":
    print("Running liquid-liquid equilibrium example...")
    lle_plot = lle_equilibrium_example()
    lle_plot.show()
    
    print("Running extraction stages example...")
    stages_plot = extraction_stages_example()
    stages_plot.show()
    
    print("Running phase diagram example...")
    phase_diagram_example()
