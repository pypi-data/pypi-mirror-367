# Extraction Triangle

A Python library for creating right triangle plots, particularly useful for **ternary (three-component) extraction data visualization**. This library provides functionality similar to ternary plots but uses right triangle geometry, making it ideal for binary and ternary extraction systems and related applications.

## Features

- **Three-Component System Support**: Full support for ternary systems (A, B, C components)
- **Solubility Envelope Curves**: Plot and interpolate binodal curves from experimental data
- **Conjugate Curves**: Draw tie line curves connecting equilibrium phases
- **Tie Line Networks**: Visualize multiple tie lines for phase equilibrium data
- Create right triangle coordinate systems with multiple orientations
- Plot data points on right triangle grids with component fraction labels
- Customizable triangle orientation and scaling
- Support for contour plots and heatmaps
- Grid lines with component fraction annotations
- Export capabilities for various formats
- Specialized methods for extraction processes

## Installation

```bash
pip install extraction-triangle
```

## Quick Start

### Basic Two-Component Plot
```python
import numpy as np
from extraction_triangle import RightTrianglePlot

# Create sample data
x_data = [0.1, 0.3, 0.5, 0.7, 0.9]
y_data = [0.8, 0.6, 0.4, 0.2, 0.1]

# Create right triangle plot
rt_plot = RightTrianglePlot()
rt_plot.scatter(x_data, y_data)
rt_plot.add_labels("Component A", "Component B")
rt_plot.show()
```

### Three-Component Extraction System
```python
# Component fractions (must sum to 1)
solute = [0.2, 0.4, 0.6]           # Component A
extract_solvent = [0.3, 0.4, 0.3]  # Component B  
raffinate_solvent = [0.5, 0.2, 0.1] # Component C

# Create ternary plot
rt_plot = RightTrianglePlot()
rt_plot.scatter_ternary(solute, extract_solvent, raffinate_solvent, 
                       c=['red', 'blue', 'green'], s=100)

# Add grid with component fraction labels
rt_plot.add_grid(show_labels=True)
rt_plot.add_labels("Solute", "Extract Solvent", "Raffinate Solvent")
rt_plot.add_corner_labels("Pure Solute", "Pure Extract", "Pure Raffinate")
rt_plot.show()
```

### Solubility Envelope and Tie Line Curves
```python
# Add solubility envelope (binodal curve) from experimental data
water_data = [0.95, 0.85, 0.70, 0.50, 0.30, 0.15, 0.05]
acetone_data = [0.04, 0.12, 0.25, 0.40, 0.55, 0.70, 0.85]
chloroform_data = [0.01, 0.03, 0.05, 0.10, 0.15, 0.15, 0.10]

# Create plot with solubility envelope curve
rt_plot = RightTrianglePlot()
rt_plot.add_solubility_envelope(water_data, acetone_data, chloroform_data,
                               interpolate=True, n_points=150,
                               color='blue', linewidth=3, 
                               fill=True, fill_alpha=0.2,
                               label='Solubility Envelope')

# Add tie line curves connecting equilibrium phases
phase1_data = {'a': [0.80, 0.65, 0.45], 'b': [0.15, 0.28, 0.42], 'c': [0.05, 0.07, 0.13]}
phase2_data = {'a': [0.10, 0.18, 0.35], 'b': [0.20, 0.35, 0.55], 'c': [0.70, 0.47, 0.10]}

rt_plot.add_tie_lines(phase1_data, phase2_data, 
                     color='red', show_points=True,
                     labels=['Aqueous Phase', 'Organic Phase'])

rt_plot.add_labels("Water", "Acetone", "Chloroform")
rt_plot.show()
```

## Triangle Coordinate System

The right triangle represents a **three-component system** where:

- **U-axis (horizontal)**: Component A fraction (0 to 1)
- **V-axis (vertical)**: Component B fraction (0 to 1) 
- **Hypotenuse**: Component C fraction = 1 - A - B

This is particularly useful for:
- **Liquid-liquid extraction**: Solute, extract solvent, raffinate solvent
- **Solubility envelope curves**: Binodal curves defining two-phase regions
- **Tie line curves**: Curved relationships between equilibrium phases
- **Mass transfer processes**: Different phase compositions
- **Chemical separations**: Multi-component mixtures

## Use Cases

- Liquid-liquid extraction diagrams with solubility envelopes
- Ternary phase equilibrium visualization with curved tie lines
- Binodal curve interpolation from experimental data
- Binary and ternary separation processes
- Chemical engineering applications
- Process optimization studies
- Selectivity and efficiency mapping

## Documentation

For detailed documentation and examples, visit: [Documentation Link]

## License

MIT License
