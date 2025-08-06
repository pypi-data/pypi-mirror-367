"""
Three-Component Extraction System Example

This example demonstrates how to use the extraction triangle library
for visualizing ternary (three-component) extraction systems.
"""

import numpy as np
import matplotlib.pyplot as plt
from extraction_triangle import RightTrianglePlot

def demo_ternary_extraction():
    """Demonstrate ternary extraction system visualization."""
    print("Creating ternary extraction system example...")
    
    # Create the plot
    rt_plot = RightTrianglePlot(figsize=(10, 10))
    
    # Example: Liquid-liquid extraction system
    # Component A: Solute (what we want to extract)
    # Component B: Extract solvent 
    # Component C: Raffinate solvent
    
    # Feed composition
    a_feed = 0.2  # 20% solute
    b_feed = 0.1  # 10% extract solvent
    c_feed = 0.7  # 70% raffinate solvent
    
    rt_plot.scatter_ternary([a_feed], [b_feed], [c_feed], 
                           c='red', s=200, marker='*', label='Feed', 
                           edgecolors='black', linewidth=2)
    
    # Extract phase composition (high in solute and extract solvent)
    a_extract = 0.6  # 60% solute
    b_extract = 0.35 # 35% extract solvent
    c_extract = 0.05 # 5% raffinate solvent
    
    rt_plot.scatter_ternary([a_extract], [b_extract], [c_extract],
                           c='blue', s=150, marker='s', label='Extract Phase',
                           edgecolors='black', linewidth=2)
    
    # Raffinate phase composition (low in solute, high in raffinate solvent)
    a_raffinate = 0.05  # 5% solute
    b_raffinate = 0.02  # 2% extract solvent
    c_raffinate = 0.93  # 93% raffinate solvent
    
    rt_plot.scatter_ternary([a_raffinate], [b_raffinate], [c_raffinate],
                           c='green', s=150, marker='s', label='Raffinate Phase',
                           edgecolors='black', linewidth=2)
    
    # Equilibrium curve data (simplified)
    n_points = 20
    a_eq = np.linspace(0.05, 0.8, n_points)
    
    # Simplified equilibrium relationship
    # In extract phase: high A, moderate B, low C
    b_eq_extract = 0.4 - 0.3 * a_eq  # B decreases as A increases
    c_eq_extract = 1 - a_eq - b_eq_extract
    
    # Filter valid points
    valid_extract = (c_eq_extract >= 0) & (c_eq_extract <= 1)
    a_eq_extract = a_eq[valid_extract]
    b_eq_extract = b_eq_extract[valid_extract]
    c_eq_extract = c_eq_extract[valid_extract]
    
    rt_plot.plot_ternary(a_eq_extract, b_eq_extract, c_eq_extract,
                        color='blue', linewidth=2, label='Extract Equilibrium',
                        alpha=0.8)
    
    # Raffinate equilibrium curve
    # In raffinate phase: low A, very low B, high C
    b_eq_raffinate = 0.05 - 0.04 * a_eq  # Very low B
    c_eq_raffinate = 1 - a_eq - b_eq_raffinate
    
    valid_raffinate = (b_eq_raffinate >= 0) & (c_eq_raffinate >= 0) & (c_eq_raffinate <= 1)
    a_eq_raffinate = a_eq[valid_raffinate]
    b_eq_raffinate = b_eq_raffinate[valid_raffinate]
    c_eq_raffinate = c_eq_raffinate[valid_raffinate]
    
    rt_plot.plot_ternary(a_eq_raffinate, b_eq_raffinate, c_eq_raffinate,
                        color='green', linewidth=2, label='Raffinate Equilibrium',
                        alpha=0.8)
    
    # Tie line connecting equilibrium phases
    tie_a = [a_extract, a_raffinate]
    tie_b = [b_extract, b_raffinate]
    tie_c = [c_extract, c_raffinate]
    
    rt_plot.plot_ternary(tie_a, tie_b, tie_c,
                        color='gray', linewidth=1.5, linestyle='--',
                        label='Tie Line', alpha=0.7)
    
    # Operating line (simplified)
    # From raffinate to extract through feed point
    n_op = 10
    t_op = np.linspace(0, 1, n_op)
    a_op = a_raffinate + t_op * (a_extract - a_raffinate)
    b_op = b_raffinate + t_op * (b_extract - b_raffinate)
    c_op = c_raffinate + t_op * (c_extract - c_raffinate)
    
    rt_plot.plot_ternary(a_op, b_op, c_op,
                        color='purple', linewidth=2, linestyle=':',
                        label='Operating Line')
    
    # Customize the plot
    rt_plot.add_grid(n_lines=10, show_labels=True, alpha=0.4)
    rt_plot.add_labels("Solute (A)", "Extract Solvent (B)", "Raffinate Solvent (C)")
    rt_plot.add_corner_labels("Pure Solute", "Pure Extract Solvent", "Pure Raffinate Solvent")
    rt_plot.set_title("Ternary Liquid-Liquid Extraction System", fontsize=14, fontweight='bold')
    rt_plot.legend(loc='center right', bbox_to_anchor=(1.3, 0.5))
    
    # Add text annotations
    rt_plot.ax.text(0.7, 0.1, 'Solute-rich\nregion', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8))
    rt_plot.ax.text(0.1, 0.8, 'Solvent-rich\nregion', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8))
    
    return rt_plot

def demo_extraction_regions():
    """Demonstrate different extraction regions and selectivity."""
    print("Creating extraction regions and selectivity example...")
    
    rt_plot = RightTrianglePlot(figsize=(10, 10))
    
    # Generate selectivity data across the triangle
    n_grid = 30
    a_vals = np.linspace(0, 1, n_grid)
    b_vals = np.linspace(0, 1, n_grid)
    
    # Create triangular grid
    a_grid = []
    b_grid = []
    selectivity = []
    
    for a in a_vals:
        for b in b_vals:
            c = 1 - a - b
            if c >= 0 and c <= 1:  # Valid ternary point
                a_grid.append(a)
                b_grid.append(b)
                
                # Example selectivity function
                # Higher selectivity when extract solvent (B) is high and raffinate solvent (C) is low
                # and there's sufficient solute (A) to extract
                sel = (a * b) / (c + 0.01)  # Avoid division by zero
                selectivity.append(sel)
    
    a_grid = np.array(a_grid)
    b_grid = np.array(b_grid)
    selectivity = np.array(selectivity)
    
    # Create filled contour plot for selectivity
    contour_filled = rt_plot.contourf(a_grid, b_grid, selectivity, 
                                     levels=15, cmap='RdYlBu_r', alpha=0.8)
    
    # Add contour lines
    contour_lines = rt_plot.contour(a_grid, b_grid, selectivity, 
                                   levels=10, colors='black', alpha=0.6, linewidths=1)
    
    # Add some operating points
    operating_points = {
        'Low Selectivity': ([0.1, 0.3, 0.2], [0.1, 0.2, 0.15], [0.8, 0.5, 0.65]),
        'High Selectivity': ([0.4, 0.6, 0.5], [0.5, 0.35, 0.45], [0.1, 0.05, 0.05]),
        'Moderate Selectivity': ([0.3, 0.4, 0.35], [0.3, 0.4, 0.35], [0.4, 0.2, 0.3])
    }
    
    colors = ['red', 'green', 'orange']
    markers = ['o', 's', '^']
    
    for i, (label, (a_pts, b_pts, c_pts)) in enumerate(operating_points.items()):
        rt_plot.scatter_ternary(a_pts, b_pts, c_pts,
                               c=colors[i], s=100, marker=markers[i], 
                               label=label, alpha=0.9, edgecolors='black')
    
    # Customize plot
    rt_plot.add_grid(n_lines=10, alpha=0.3)
    rt_plot.add_labels("Solute", "Extract Solvent", "Raffinate Solvent")
    rt_plot.add_corner_labels()
    rt_plot.set_title("Extraction Selectivity Map", fontsize=14, fontweight='bold')
    rt_plot.add_colorbar(contour_filled, label='Selectivity')
    rt_plot.legend()
    
    return rt_plot

def demo_process_optimization():
    """Demonstrate process optimization using triangle plots."""
    print("Creating process optimization example...")
    
    rt_plot = RightTrianglePlot(figsize=(12, 10))
    
    # Multi-stage extraction process
    stages = {
        'Feed': ([0.25], [0.05], [0.70]),
        'Stage 1': ([0.35], [0.15], [0.50]),
        'Stage 2': ([0.45], [0.25], [0.30]),
        'Stage 3': ([0.55], [0.35], [0.10]),
        'Final Extract': ([0.65], [0.30], [0.05])
    }
    
    colors = ['red', 'orange', 'yellow', 'lightgreen', 'green']
    sizes = [200, 150, 150, 150, 200]
    
    # Plot stages
    a_path = []
    b_path = []
    c_path = []
    
    for i, (stage, (a, b, c)) in enumerate(stages.items()):
        rt_plot.scatter_ternary(a, b, c, c=colors[i], s=sizes[i], 
                               marker='o' if stage != 'Final Extract' else '*',
                               label=stage, edgecolors='black', linewidth=2)
        a_path.extend(a)
        b_path.extend(b)
        c_path.extend(c)
    
    # Draw process path
    rt_plot.plot_ternary(a_path, b_path, c_path, 
                        color='black', linewidth=3, alpha=0.7, 
                        label='Process Path')
    
    # Add efficiency contours
    n_grid = 25
    a_vals = np.linspace(0, 0.8, n_grid)
    b_vals = np.linspace(0, 0.6, n_grid)
    
    a_grid = []
    b_grid = []
    efficiency = []
    
    for a in a_vals:
        for b in b_vals:
            c = 1 - a - b
            if c >= 0 and c <= 1:
                a_grid.append(a)
                b_grid.append(b)
                # Efficiency function (higher with more solute extracted)
                eff = a * (1 - c) * 100  # Percentage efficiency
                efficiency.append(eff)
    
    a_grid = np.array(a_grid)
    b_grid = np.array(b_grid)
    efficiency = np.array(efficiency)
    
    # Add efficiency contours
    contour_eff = rt_plot.contour(a_grid, b_grid, efficiency, 
                                 levels=[20, 40, 60, 80], 
                                 colors='blue', alpha=0.6, linewidths=1.5)
    
    plt.clabel(contour_eff, inline=True, fontsize=9, fmt='%d%% eff')
    
    # Customize
    rt_plot.add_grid(n_lines=10, alpha=0.3)
    rt_plot.add_labels("Solute Concentration", "Extract Solvent", "Raffinate Solvent")
    rt_plot.set_title("Multi-Stage Extraction Process Optimization", fontsize=14, fontweight='bold')
    rt_plot.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
    
    return rt_plot

if __name__ == "__main__":
    print("=" * 60)
    print("Three-Component Extraction System Examples")
    print("=" * 60)
    
    # Run demonstrations
    plot1 = demo_ternary_extraction()
    plot1.show()
    
    plot2 = demo_extraction_regions()
    plot2.show()
    
    plot3 = demo_process_optimization()
    plot3.show()
    
    print("\nAll ternary extraction examples completed!")
    print("Each plot shows different aspects of three-component extraction systems.")
