"""
Solubility Envelope and Tie Lines Example

This example demonstrates the new functionality for plotting solubility envelopes (binodal curves),
tie lines, and plait points in extraction systems.
"""

import numpy as np
import matplotlib.pyplot as plt
from extraction_triangle import RightTrianglePlot

def demo_solubility_envelope():
    """Demonstrate solubility envelope functionality."""
    print("Creating solubility envelope example...")
    
    rt_plot = RightTrianglePlot(figsize=(12, 10))
    
    # Example solubility data for a water-acetone-chloroform system
    # Component A: Water, Component B: Acetone, Component C: Chloroform
    
    # Solubility envelope data points (simplified example)
    water_envelope = np.array([0.98, 0.90, 0.75, 0.60, 0.45, 0.30, 0.20, 0.15, 0.12, 0.10, 0.08, 0.06, 0.05, 0.04, 0.03, 0.02])
    acetone_envelope = np.array([0.01, 0.08, 0.20, 0.30, 0.40, 0.50, 0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85, 0.88, 0.90, 0.92])
    chloroform_envelope = 1 - water_envelope - acetone_envelope
    
    # Add solubility envelope with interpolation
    envelope_line = rt_plot.add_solubility_envelope(
        water_envelope, acetone_envelope, chloroform_envelope,
        interpolate=True, n_points=150,
        color='blue', linewidth=3, 
        fill=True, fill_alpha=0.2,
        label='Solubility Envelope (Binodal Curve)'
    )
    
    # Add some tie line data (equilibrium compositions)
    tie_line_data = {
        'water_rich': {
            'a': [0.85, 0.75, 0.65, 0.55, 0.45],  # Water in water-rich phase
            'b': [0.12, 0.20, 0.28, 0.35, 0.42],  # Acetone in water-rich phase
            'c': [0.03, 0.05, 0.07, 0.10, 0.13]   # Chloroform in water-rich phase
        },
        'chloroform_rich': {
            'a': [0.08, 0.12, 0.18, 0.25, 0.35],  # Water in chloroform-rich phase
            'b': [0.15, 0.25, 0.35, 0.45, 0.55],  # Acetone in chloroform-rich phase
            'c': [0.77, 0.63, 0.47, 0.30, 0.10]   # Chloroform in chloroform-rich phase
        }
    }
    
    # Add tie lines
    tie_lines = rt_plot.add_tie_lines(
        tie_line_data['water_rich'], 
        tie_line_data['chloroform_rich'],
        color='red', linewidth=1.5, alpha=0.7,
        show_points=True, 
        point_colors=['lightblue', 'orange'],
        point_sizes=[80, 80],
        labels=['Water-Rich Phase', 'Chloroform-Rich Phase']
    )
    
    # Add plait point (critical point where phases become identical)
    rt_plot.add_plait_point(0.35, 0.55, 0.10, 
                           color='purple', size=200, marker='*',
                           label='Plait Point')
    
    # Add a feed point
    feed_water = 0.40
    feed_acetone = 0.35
    feed_chloroform = 0.25
    
    rt_plot.scatter_ternary([feed_water], [feed_acetone], [feed_chloroform],
                           c='green', s=150, marker='D', 
                           label='Feed Composition', 
                           edgecolors='darkgreen', linewidth=2)
    
    # Customize plot
    rt_plot.add_grid(show_labels=True, alpha=0.3)
    rt_plot.add_labels("Water", "Acetone", "Chloroform")
    rt_plot.add_corner_labels("Pure Water", "Pure Acetone", "Pure Chloroform")
    rt_plot.set_title("Liquid-Liquid Equilibrium: Water-Acetone-Chloroform System", 
                     fontsize=14, fontweight='bold')
    rt_plot.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
    
    # Add text annotations
    rt_plot.ax.text(0.6, 0.15, 'Two-Phase\nRegion', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.8),
                   fontsize=12, fontweight='bold')
    
    rt_plot.ax.text(0.2, 0.7, 'Single-Phase\nRegion', ha='center', va='center',
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.8),
                   fontsize=12, fontweight='bold')
    
    return rt_plot

def demo_extraction_process_design():
    """Demonstrate extraction process design using solubility data."""
    print("Creating extraction process design example...")
    
    rt_plot = RightTrianglePlot(figsize=(12, 10))
    
    # Simplified ternary system: Acetic Acid (A) - Water (B) - Ethyl Acetate (C)
    
    # Solubility envelope (simplified data)
    n_env = 20
    theta = np.linspace(0, np.pi/2, n_env)
    
    # Create a realistic-looking envelope
    acid_env = 0.05 + 0.9 * (1 - np.cos(theta))**1.5
    water_env = 0.95 * np.sin(theta)**2
    acetate_env = 1 - acid_env - water_env
    
    # Ensure valid fractions
    total = acid_env + water_env + acetate_env
    acid_env /= total
    water_env /= total
    acetate_env /= total
    
    # Add extraction region
    envelope_data = {
        'a': acid_env,
        'b': water_env, 
        'c': acetate_env
    }
    
    rt_plot.add_extraction_region(
        envelope_data, 
        fill_color='lightcyan', 
        fill_alpha=0.3,
        boundary_color='darkblue',
        boundary_linewidth=3,
        label='Two-Phase Region'
    )
    
    # Multiple stage extraction process
    stages = {
        'Feed': {'a': 0.30, 'b': 0.65, 'c': 0.05},
        'Extract_1': {'a': 0.45, 'b': 0.35, 'c': 0.20},
        'Raffinate_1': {'a': 0.15, 'b': 0.80, 'c': 0.05},
        'Extract_2': {'a': 0.60, 'b': 0.25, 'c': 0.15},
        'Raffinate_2': {'a': 0.08, 'b': 0.87, 'c': 0.05},
        'Final_Extract': {'a': 0.70, 'b': 0.20, 'c': 0.10}
    }
    
    stage_colors = ['red', 'orange', 'yellow', 'lightgreen', 'green', 'blue']
    stage_markers = ['*', 's', 'o', 's', 'o', 'D']
    stage_sizes = [200, 120, 100, 120, 100, 150]
    
    # Plot process stages
    for i, (stage_name, composition) in enumerate(stages.items()):
        rt_plot.scatter_ternary(
            [composition['a']], [composition['b']], [composition['c']],
            c=stage_colors[i], s=stage_sizes[i], marker=stage_markers[i],
            label=stage_name.replace('_', ' '), 
            edgecolors='black', linewidth=1.5, alpha=0.9
        )
    
    # Add operating lines between stages
    operating_lines = [
        ('Feed', 'Extract_1', 'Raffinate_1'),
        ('Raffinate_1', 'Extract_2', 'Raffinate_2'),
        ('Extract_1', 'Final_Extract')
    ]
    
    for line_data in operating_lines:
        if len(line_data) == 3:  # Tie line
            stage1, extract, raffinate = line_data
            rt_plot.add_conjugate_line(
                stages[extract]['a'], stages[extract]['b'], stages[extract]['c'],
                stages[raffinate]['a'], stages[raffinate]['b'], stages[raffinate]['c'],
                color='purple', linewidth=2, linestyle='--', alpha=0.8
            )
        else:  # Operating line
            stage1, stage2 = line_data
            rt_plot.plot_ternary(
                [stages[stage1]['a'], stages[stage2]['a']],
                [stages[stage1]['b'], stages[stage2]['b']],
                [stages[stage1]['c'], stages[stage2]['c']],
                color='darkred', linewidth=2.5, alpha=0.8
            )
    
    # Add equilibrium data points on the envelope
    eq_points_a = np.array([0.15, 0.25, 0.35, 0.45, 0.55, 0.65])
    eq_points_b = np.array([0.75, 0.60, 0.45, 0.35, 0.28, 0.22])
    eq_points_c = 1 - eq_points_a - eq_points_b
    
    rt_plot.scatter_ternary(eq_points_a, eq_points_b, eq_points_c,
                           c='navy', s=40, marker='o', alpha=0.8,
                           label='Equilibrium Data Points')
    
    # Customize plot
    rt_plot.add_grid(n_lines=10, show_labels=True, alpha=0.3)
    rt_plot.add_labels("Acetic Acid", "Water", "Ethyl Acetate")
    rt_plot.add_corner_labels("Pure Acid", "Pure Water", "Pure Ethyl Acetate")
    rt_plot.set_title("Multi-Stage Liquid-Liquid Extraction Process Design", 
                     fontsize=14, fontweight='bold')
    rt_plot.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
    
    return rt_plot

def demo_tie_line_correlation():
    """Demonstrate tie line correlation and interpolation."""
    print("Creating tie line correlation example...")
    
    rt_plot = RightTrianglePlot(figsize=(12, 10))
    
    # Example system with known tie line data
    # Create a series of tie lines with realistic distribution
    
    n_ties = 8
    
    # Phase 1 (aqueous phase) - high in water, low in organic
    phase1_data = {
        'a': np.array([0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45]),  # Solute
        'b': np.array([0.85, 0.80, 0.75, 0.68, 0.60, 0.52, 0.45, 0.38]),  # Water
        'c': np.array([0.05, 0.05, 0.05, 0.07, 0.10, 0.13, 0.15, 0.17])   # Organic solvent
    }
    
    # Phase 2 (organic phase) - high in organic, low in water
    phase2_data = {
        'a': np.array([0.25, 0.35, 0.45, 0.55, 0.65, 0.72, 0.78, 0.82]),  # Solute
        'b': np.array([0.15, 0.18, 0.20, 0.22, 0.18, 0.15, 0.12, 0.10]),  # Water
        'c': np.array([0.60, 0.47, 0.35, 0.23, 0.17, 0.13, 0.10, 0.08])   # Organic solvent
    }
    
    # Create solubility envelope from tie line endpoints
    all_a = np.concatenate([phase1_data['a'], phase2_data['a'][::-1]])
    all_b = np.concatenate([phase1_data['b'], phase2_data['b'][::-1]])
    all_c = np.concatenate([phase1_data['c'], phase2_data['c'][::-1]])
    
    # Add solubility envelope
    rt_plot.add_solubility_envelope(
        all_a, all_b, all_c,
        interpolate=True, n_points=100,
        color='darkblue', linewidth=3,
        fill=True, fill_alpha=0.15,
        label='Solubility Envelope'
    )
    
    # Add tie lines with correlation
    rt_plot.add_tie_lines(
        phase1_data, phase2_data,
        color='red', linewidth=1.5, alpha=0.8,
        show_points=True,
        point_colors=['lightblue', 'orange'],
        point_sizes=[70, 70],
        point_markers=['o', 's'],
        labels=['Aqueous Phase', 'Organic Phase']
    )
    
    # Add plait point estimation
    plait_a = (phase1_data['a'][-1] + phase2_data['a'][-1]) / 2
    plait_b = (phase1_data['b'][-1] + phase2_data['b'][-1]) / 2
    plait_c = (phase1_data['c'][-1] + phase2_data['c'][-1]) / 2
    
    rt_plot.add_plait_point(plait_a, plait_b, plait_c,
                           color='purple', size=180, marker='*',
                           label='Estimated Plait Point')
    
    # Add distribution coefficient lines (K = C_organic/C_aqueous)
    # Show lines of constant distribution coefficient
    k_values = [0.5, 1.0, 2.0, 5.0]
    colors = ['green', 'orange', 'red', 'purple']
    
    for k, color in zip(k_values, colors):
        # Create points along constant K lines
        a_aq = np.linspace(0.1, 0.45, 20)
        a_org = k * a_aq
        
        # Filter valid points
        valid = (a_org <= 0.85) & (a_org >= 0.1)
        a_aq_valid = a_aq[valid]
        a_org_valid = a_org[valid]
        
        if len(a_aq_valid) > 1:
            # Simple linear relationship for demonstration
            b_aq = 0.9 - a_aq_valid
            b_org = 0.2 - 0.1 * a_org_valid
            c_aq = 1 - a_aq_valid - b_aq
            c_org = 1 - a_org_valid - b_org
            
            # Ensure valid fractions
            c_aq = np.clip(c_aq, 0, 1)
            c_org = np.clip(c_org, 0, 1)
            
            # Plot K-line points
            for i in range(0, len(a_aq_valid), 3):
                if i < len(a_aq_valid):
                    rt_plot.add_conjugate_line(
                        a_aq_valid[i], b_aq[i], c_aq[i],
                        a_org_valid[i], b_org[i], c_org[i],
                        color=color, linewidth=1, linestyle=':', alpha=0.6,
                        label=f'K = {k}' if i == 0 else None
                    )
    
    # Customize plot
    rt_plot.add_grid(show_labels=True, alpha=0.3)
    rt_plot.add_labels("Solute", "Water", "Organic Solvent")
    rt_plot.set_title("Tie Line Correlation and Distribution Coefficients", 
                     fontsize=14, fontweight='bold')
    rt_plot.legend(bbox_to_anchor=(1.15, 1), loc='upper left')
    
    return rt_plot

if __name__ == "__main__":
    print("=" * 70)
    print("Solubility Envelope and Tie Lines Examples")
    print("=" * 70)
    
    # Run demonstrations
    plot1 = demo_solubility_envelope()
    plot1.show()
    
    plot2 = demo_extraction_process_design()
    plot2.show()
    
    plot3 = demo_tie_line_correlation()
    plot3.show()
    
    print("\nAll solubility envelope and tie line examples completed!")
    print("Features demonstrated:")
    print("- Solubility envelope with interpolation")
    print("- Tie lines (conjugate curves)")
    print("- Multiple tie lines with phase points")
    print("- Plait point marking")
    print("- Extraction region highlighting")
    print("- Distribution coefficient visualization")
