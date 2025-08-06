"""
Right Triangle Plot Module

Main plotting functionality for right triangle coordinate systems.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.collections import LineCollection
from typing import Union, Optional, List, Tuple, Dict, Any
import warnings

from .coordinates import RightTriangleCoordinates
from .utils import validate_data, normalize_data, check_triangle_bounds


class RightTrianglePlot:
    """
    Main class for creating right triangle plots.
    
    This class provides a matplotlib-based interface for plotting data
    in right triangle coordinate systems, particularly useful for
    extraction and separation process visualization.
    """
    
    def __init__(self, orientation: str = "bottom-left", figsize: Tuple[float, float] = (8, 8)):
        """
        Initialize the right triangle plot.
        
        Parameters:
        -----------
        orientation : str
            Triangle orientation ('bottom-left', 'bottom-right', 'top-left', 'top-right')
        figsize : tuple
            Figure size (width, height) in inches
        """
        self.coordinates = RightTriangleCoordinates(orientation)
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self._setup_plot()
        
    def _setup_plot(self):
        """Setup the basic plot properties."""
        self.ax.set_aspect('equal')
        self.ax.set_xlim(-0.1, 1.1)
        self.ax.set_ylim(-0.1, 1.1)
        self._draw_triangle_boundary()
        
    def _draw_triangle_boundary(self, color: str = 'black', linewidth: float = 2.0):
        """Draw the triangle boundary."""
        x_vertices, y_vertices = self.coordinates.get_triangle_vertices()
        self.ax.plot(x_vertices, y_vertices, color=color, linewidth=linewidth)
        
    def scatter(self, u: Union[List, np.ndarray], v: Union[List, np.ndarray], 
                c: Optional[Union[str, List, np.ndarray]] = None,
                s: Union[float, List, np.ndarray] = 20,
                alpha: float = 0.7,
                marker: str = 'o',
                label: Optional[str] = None,
                **kwargs) -> plt.scatter:
        """
        Create a scatter plot in right triangle coordinates.
        
        Parameters:
        -----------
        u, v : array-like
            Right triangle coordinates
        c : color, array-like, optional
            Colors for the points
        s : float or array-like
            Sizes for the points
        alpha : float
            Transparency level
        marker : str
            Marker style
        label : str, optional
            Label for legend
        **kwargs
            Additional arguments passed to matplotlib scatter
            
        Returns:
        --------
        scatter : matplotlib PathCollection
            The scatter plot object
        """
        u = validate_data(u)
        v = validate_data(v)
        
        # Check bounds and warn if points are outside
        inside = self.coordinates.is_inside_triangle(u, v)
        if not np.all(inside):
            warnings.warn(f"{np.sum(~inside)} points are outside the triangle and will be clipped")
            u, v = check_triangle_bounds(u, v)
        
        # Convert to Cartesian coordinates
        x, y = self.coordinates.to_cartesian(u, v)
        
        return self.ax.scatter(x, y, c=c, s=s, alpha=alpha, marker=marker, label=label, **kwargs)
    
    def plot(self, u: Union[List, np.ndarray], v: Union[List, np.ndarray],
             color: str = 'blue',
             linewidth: float = 1.5,
             linestyle: str = '-',
             alpha: float = 0.8,
             label: Optional[str] = None,
             **kwargs) -> plt.Line2D:
        """
        Create a line plot in right triangle coordinates.
        
        Parameters:
        -----------
        u, v : array-like
            Right triangle coordinates
        color : str
            Line color
        linewidth : float
            Line width
        linestyle : str
            Line style
        alpha : float
            Transparency level
        label : str, optional
            Label for legend
        **kwargs
            Additional arguments passed to matplotlib plot
            
        Returns:
        --------
        line : matplotlib Line2D
            The line plot object
        """
        u = validate_data(u)
        v = validate_data(v)
        
        # Convert to Cartesian coordinates
        x, y = self.coordinates.to_cartesian(u, v)
        
        line, = self.ax.plot(x, y, color=color, linewidth=linewidth, 
                            linestyle=linestyle, alpha=alpha, label=label, **kwargs)
        return line
    
    def contour(self, u_grid: np.ndarray, v_grid: np.ndarray, z_values: np.ndarray,
                levels: Optional[Union[int, List]] = None,
                colors: Optional[str] = None,
                alpha: float = 0.6,
                **kwargs) -> plt.contour:
        """
        Create contour plot in right triangle coordinates.
        
        Parameters:
        -----------
        u_grid, v_grid : np.ndarray
            Grid coordinates in triangle space
        z_values : np.ndarray
            Values to contour
        levels : int or list, optional
            Contour levels
        colors : str, optional
            Contour colors
        alpha : float
            Transparency level
        **kwargs
            Additional arguments passed to matplotlib contour
            
        Returns:
        --------
        contour : matplotlib ContourSet
            The contour plot object
        """
        # Convert grid to Cartesian
        x_grid, y_grid = self.coordinates.to_cartesian(u_grid, v_grid)
        
        # Create regular grid for interpolation
        xi = np.linspace(0, 1, 50)
        yi = np.linspace(0, 1, 50)
        X, Y = np.meshgrid(xi, yi)
        
        # Interpolate values to regular grid
        from scipy.interpolate import griddata
        Z = griddata((x_grid, y_grid), z_values, (X, Y), method='linear')
        
        # Mask points outside triangle
        U, V = self.coordinates.from_cartesian(X, Y)
        inside = self.coordinates.is_inside_triangle(U, V)
        Z = np.where(inside, Z, np.nan)
        
        return self.ax.contour(X, Y, Z, levels=levels, colors=colors, alpha=alpha, **kwargs)
    
    def contourf(self, u_grid: np.ndarray, v_grid: np.ndarray, z_values: np.ndarray,
                 levels: Optional[Union[int, List]] = None,
                 cmap: Optional[str] = None,
                 alpha: float = 0.6,
                 **kwargs) -> plt.contourf:
        """
        Create filled contour plot in right triangle coordinates.
        
        Parameters:
        -----------
        u_grid, v_grid : np.ndarray
            Grid coordinates in triangle space
        z_values : np.ndarray
            Values to contour
        levels : int or list, optional
            Contour levels
        cmap : str, optional
            Colormap name
        alpha : float
            Transparency level
        **kwargs
            Additional arguments passed to matplotlib contourf
            
        Returns:
        --------
        contourf : matplotlib ContourSet
            The filled contour plot object
        """
        # Convert grid to Cartesian
        x_grid, y_grid = self.coordinates.to_cartesian(u_grid, v_grid)
        
        # Create regular grid for interpolation
        xi = np.linspace(0, 1, 50)
        yi = np.linspace(0, 1, 50)
        X, Y = np.meshgrid(xi, yi)
        
        # Interpolate values to regular grid
        from scipy.interpolate import griddata
        Z = griddata((x_grid, y_grid), z_values, (X, Y), method='linear')
        
        # Mask points outside triangle
        U, V = self.coordinates.from_cartesian(X, Y)
        inside = self.coordinates.is_inside_triangle(U, V)
        Z = np.where(inside, Z, np.nan)
        
        return self.ax.contourf(X, Y, Z, levels=levels, cmap=cmap, alpha=alpha, **kwargs)
    
    def add_grid(self, n_lines: int = 10, alpha: float = 0.3, color: str = 'gray', 
                 show_labels: bool = False, label_fontsize: int = 8):
        """
        Add grid lines to the triangle plot with optional component fraction labels.
        
        Parameters:
        -----------
        n_lines : int
            Number of grid lines in each direction
        alpha : float
            Grid line transparency
        color : str
            Grid line color
        show_labels : bool
            Whether to show component fraction labels on grid lines
        label_fontsize : int
            Font size for grid labels
        """
        # Simple grid implementation - draw lines at regular intervals
        for i in range(1, n_lines):
            t = i / n_lines
            
            # Lines parallel to the base (horizontal) - constant Component B
            if t < 1:
                x_line = [0, 1-t]
                y_line = [t, t]
                self.ax.plot(x_line, y_line, color=color, alpha=alpha, linewidth=0.5)
                if show_labels:
                    self.ax.text(-0.02, t, f'{t:.1f}', ha='right', va='center', 
                               fontsize=label_fontsize, alpha=0.7)
            
            # Lines parallel to the left side (vertical) - constant Component A
            if t < 1:
                x_line = [t, t]
                y_line = [0, 1-t]
                self.ax.plot(x_line, y_line, color=color, alpha=alpha, linewidth=0.5)
                if show_labels:
                    self.ax.text(t, -0.02, f'{t:.1f}', ha='center', va='top', 
                               fontsize=label_fontsize, alpha=0.7)
            
            # Lines parallel to the hypotenuse - constant Component C
            if t < 1:
                x_line = [0, t]
                y_line = [t, 0]
                self.ax.plot(x_line, y_line, color=color, alpha=alpha, linewidth=0.5)
                if show_labels:
                    # Component C fraction = 1 - u - v = 1 - t (along this line)
                    c_fraction = 1 - t
                    mid_x, mid_y = t/2, t/2
                    self.ax.text(mid_x + 0.02, mid_y + 0.02, f'{c_fraction:.1f}', 
                               ha='left', va='bottom', fontsize=label_fontsize, alpha=0.7)
    
    def add_labels(self, u_label: str = "Component A", v_label: str = "Component B", 
                   w_label: str = "Component C", fontsize: int = 12, offset: float = 0.05):
        """
        Add axis labels to the triangle for three-component system.
        
        Parameters:
        -----------
        u_label, v_label, w_label : str
            Labels for the three components (A, B, C)
        fontsize : int
            Font size for labels
        offset : float
            Offset distance from triangle edges
        """
        if self.coordinates.orientation == "bottom-left":
            # U-axis label (bottom edge) - Component A
            self.ax.text(0.5, -offset, u_label, ha='center', va='top', fontsize=fontsize)
            # V-axis label (left edge) - Component B
            self.ax.text(-offset, 0.5, v_label, ha='right', va='center', fontsize=fontsize, rotation=90)
            # W-axis label (hypotenuse) - Component C
            self.ax.text(0.6, 0.6, w_label, ha='center', va='center', fontsize=fontsize, rotation=-45)
        # Add other orientations as needed
    
    def add_colorbar(self, mappable, **kwargs):
        """Add a colorbar to the plot."""
        return self.fig.colorbar(mappable, ax=self.ax, **kwargs)
    
    def legend(self, **kwargs):
        """Add legend to the plot."""
        return self.ax.legend(**kwargs)
    
    def set_title(self, title: str, **kwargs):
        """Set plot title."""
        self.ax.set_title(title, **kwargs)
    
    def show(self):
        """Display the plot."""
        plt.show()
    
    def save(self, filename: str, **kwargs):
        """Save the plot to file."""
        self.fig.savefig(filename, **kwargs)
    
    def get_third_component(self, u: Union[List, np.ndarray], v: Union[List, np.ndarray]) -> np.ndarray:
        """
        Calculate the third component fraction for ternary systems.
        
        Parameters:
        -----------
        u, v : array-like
            First and second component fractions
            
        Returns:
        --------
        w : np.ndarray
            Third component fraction (w = 1 - u - v)
        """
        u = np.asarray(u)
        v = np.asarray(v)
        return 1 - u - v
    
    def scatter_ternary(self, a: Union[List, np.ndarray], b: Union[List, np.ndarray], 
                       component_c: Union[List, np.ndarray], normalize: bool = True, **kwargs):
        """
        Create a scatter plot for ternary (three-component) data.
        
        Parameters:
        -----------
        a, b, component_c : array-like
            Fractions of components A, B, and C
        normalize : bool
            Whether to normalize so that a + b + component_c = 1
        **kwargs
            Additional arguments passed to scatter method
            
        Returns:
        --------
        scatter : matplotlib PathCollection
            The scatter plot object
        """
        a = np.asarray(a)
        b = np.asarray(b)
        component_c = np.asarray(component_c)
        
        if normalize:
            # Normalize to ensure a + b + component_c = 1
            total = a + b + component_c
            a = a / total
            b = b / total
            component_c = component_c / total
        
        # Check if data represents valid fractions
        if not np.allclose(a + b + component_c, 1.0, atol=1e-6):
            warnings.warn("Component fractions do not sum to 1. Consider setting normalize=True")
        
        # Convert to triangle coordinates (a=u, b=v)
        return self.scatter(a, b, **kwargs)
    
    def plot_ternary(self, a: Union[List, np.ndarray], b: Union[List, np.ndarray], 
                    component_c: Union[List, np.ndarray], normalize: bool = True, **kwargs):
        """
        Create a line plot for ternary (three-component) data.
        
        Parameters:
        -----------
        a, b, component_c : array-like
            Fractions of components A, B, and C
        normalize : bool
            Whether to normalize so that a + b + component_c = 1
        **kwargs
            Additional arguments passed to plot method
            
        Returns:
        --------
        line : matplotlib Line2D
            The line plot object
        """
        a = np.asarray(a)
        b = np.asarray(b)
        component_c = np.asarray(component_c)
        
        if normalize:
            # Normalize to ensure a + b + component_c = 1
            total = a + b + component_c
            a = a / total
            b = b / total
            component_c = component_c / total
        
        # Check if data represents valid fractions
        if not np.allclose(a + b + component_c, 1.0, atol=1e-6):
            warnings.warn("Component fractions do not sum to 1. Consider setting normalize=True")
        
        # Convert to triangle coordinates (a=u, b=v)
        return self.plot(a, b, **kwargs)
    
    def add_corner_labels(self, a_label: str = "A = 1.0", b_label: str = "B = 1.0", 
                         c_label: str = "C = 1.0", fontsize: int = 10, fontweight: str = 'bold'):
        """
        Add labels at the triangle corners to show pure component positions.
        
        Parameters:
        -----------
        a_label, b_label, c_label : str
            Labels for pure components at each corner
        fontsize : int
            Font size for corner labels
        fontweight : str
            Font weight for corner labels
        """
        if self.coordinates.orientation == "bottom-left":
            # Pure A at bottom-right corner (1, 0)
            self.ax.text(1.05, -0.02, a_label, ha='left', va='top', 
                        fontsize=fontsize, fontweight=fontweight)
            # Pure B at top-left corner (0, 1)
            self.ax.text(-0.05, 1.02, b_label, ha='right', va='bottom', 
                        fontsize=fontsize, fontweight=fontweight)
            # Pure C at bottom-left corner (0, 0)
            self.ax.text(-0.05, -0.02, c_label, ha='right', va='top', 
                        fontsize=fontsize, fontweight=fontweight)
    
    def add_solubility_envelope(self, a_data: Union[List, np.ndarray], b_data: Union[List, np.ndarray], 
                               component_c_data: Union[List, np.ndarray] = None,
                               interpolate: bool = True, n_points: int = 100,
                               color: str = 'blue', linewidth: float = 2.0, 
                               linestyle: str = '-', alpha: float = 0.8,
                               fill: bool = False, fill_alpha: float = 0.2,
                               label: str = 'Solubility Envelope', **kwargs):
        """
        Add a solubility envelope (binodal curve) to the plot.
        
        The solubility envelope is a curved boundary that separates the single-phase 
        region from the two-phase region in a ternary system. This curve is typically
        determined experimentally and defines the compositions where phase separation occurs.
        
        Parameters:
        -----------
        a_data, b_data : array-like
            Component A and B fractions for known solubility points along the curve
        component_c_data : array-like, optional
            Component C fractions. If None, calculated as 1 - a - b
        interpolate : bool
            Whether to interpolate between points for smooth curve generation
        n_points : int
            Number of points for interpolation to create smooth curve
        color : str
            Curve color
        linewidth : float
            Curve line width
        linestyle : str
            Curve line style
        alpha : float
            Curve transparency
        fill : bool
            Whether to fill the area inside the envelope curve
        fill_alpha : float
            Fill transparency
        label : str
            Label for legend
        **kwargs
            Additional arguments passed to plot method
            
        Returns:
        --------
        line : matplotlib Line2D
            The envelope curve object
        """
        a_data = np.asarray(a_data)
        b_data = np.asarray(b_data)
        
        if component_c_data is None:
            component_c_data = 1 - a_data - b_data
        else:
            component_c_data = np.asarray(component_c_data)
        
        if interpolate and len(a_data) > 2:
            # Sort points for better interpolation
            sort_idx = np.argsort(a_data)
            a_sorted = a_data[sort_idx]
            b_sorted = b_data[sort_idx]
            c_sorted = component_c_data[sort_idx]
            
            # Interpolate using spline
            from scipy.interpolate import interp1d
            
            # Create parameter for interpolation
            t = np.linspace(0, 1, len(a_sorted))
            t_new = np.linspace(0, 1, n_points)
            
            # Interpolate each component
            f_a = interp1d(t, a_sorted, kind='cubic', bounds_error=False, fill_value='extrapolate')
            f_b = interp1d(t, b_sorted, kind='cubic', bounds_error=False, fill_value='extrapolate')
            
            a_interp = f_a(t_new)
            b_interp = f_b(t_new)
            c_interp = 1 - a_interp - b_interp
            
            # Ensure valid fractions
            a_interp = np.clip(a_interp, 0, 1)
            b_interp = np.clip(b_interp, 0, 1)
            c_interp = np.clip(c_interp, 0, 1)
            
            # Normalize to ensure sum = 1
            total = a_interp + b_interp + c_interp
            a_interp /= total
            b_interp /= total
            c_interp /= total
            
        else:
            a_interp = a_data
            b_interp = b_data
            c_interp = component_c_data
        
        # Plot the envelope curve
        line = self.plot_ternary(a_interp, b_interp, c_interp, 
                                color=color, linewidth=linewidth, linestyle=linestyle,
                                alpha=alpha, label=label, **kwargs)
        
        # Fill area if requested
        if fill:
            x, y = self.coordinates.to_cartesian(a_interp, b_interp)
            self.ax.fill(x, y, color=color, alpha=fill_alpha)
        
        return line
    
    def add_conjugate_line(self, a1: float, b1: float, c1: float,
                          a2: float, b2: float, c2: float,
                          color: str = 'red', linewidth: float = 1.5,
                          linestyle: str = '--', alpha: float = 0.8,
                          label: str = 'Tie Line', **kwargs):
        """
        Add a tie line connecting two equilibrium phases.
        
        A tie line connects the compositions of two phases that are in equilibrium
        with each other. In ternary systems, these are typically straight lines,
        but the overall pattern of multiple tie lines forms curved relationships
        across the phase diagram.
        
        Parameters:
        -----------
        a1, b1, c1 : float
            Component fractions for first equilibrium phase
        a2, b2, c2 : float
            Component fractions for second equilibrium phase
        color : str
            Line color
        linewidth : float
            Line width
        linestyle : str
            Line style
        alpha : float
            Line transparency
        label : str
            Label for legend
        **kwargs
            Additional arguments passed to plot method
            
        Returns:
        --------
        line : matplotlib Line2D
            The tie line object
        """
        # Normalize fractions
        total1 = a1 + b1 + c1
        total2 = a2 + b2 + c2
        
        a_line = [a1/total1, a2/total2]
        b_line = [b1/total1, b2/total2]
        c_line = [c1/total1, c2/total2]
        
        return self.plot_ternary(a_line, b_line, c_line,
                               color=color, linewidth=linewidth, linestyle=linestyle,
                               alpha=alpha, label=label, **kwargs)
    
    def add_tie_lines(self, phase1_data: Dict[str, Union[List, np.ndarray]], 
                     phase2_data: Dict[str, Union[List, np.ndarray]],
                     color: str = 'gray', linewidth: float = 1.0,
                     linestyle: str = '-', alpha: float = 0.6,
                     show_points: bool = True, point_colors: List[str] = ['blue', 'red'],
                     point_sizes: List[float] = [50, 50], point_markers: List[str] = ['o', 's'],
                     labels: List[str] = ['Phase 1', 'Phase 2'], **kwargs):
        """
        Add multiple tie lines between equilibrium phases.
        
        This method creates a network of tie lines that, when viewed together,
        show the curved relationship between equilibrium phases across the
        composition space. Each individual tie line is straight, but the
        envelope of all tie lines forms curved patterns characteristic
        of the specific ternary system.
        
        Parameters:
        -----------
        phase1_data : dict
            Dictionary with keys 'a', 'b', 'c' containing component fractions for phase 1
        phase2_data : dict
            Dictionary with keys 'a', 'b', 'c' containing component fractions for phase 2
        color : str
            Tie line color
        linewidth : float
            Tie line width
        linestyle : str
            Tie line style
        alpha : float
            Tie line transparency
        show_points : bool
            Whether to show phase composition points
        point_colors : list
            Colors for phase points
        point_sizes : list
            Sizes for phase points
        point_markers : list
            Markers for phase points
        labels : list
            Labels for phases
        **kwargs
            Additional arguments passed to plot method
            
        Returns:
        --------
        lines : list
            List of tie line objects
        """
        a1_data = np.asarray(phase1_data['a'])
        b1_data = np.asarray(phase1_data['b'])
        c1_data = np.asarray(phase1_data['c'])
        
        a2_data = np.asarray(phase2_data['a'])
        b2_data = np.asarray(phase2_data['b'])
        c2_data = np.asarray(phase2_data['c'])
        
        if len(a1_data) != len(a2_data):
            raise ValueError("Phase 1 and Phase 2 must have the same number of data points")
        
        lines = []
        
        # Add individual tie lines
        for i in range(len(a1_data)):
            line = self.add_conjugate_line(
                a1_data[i], b1_data[i], c1_data[i],
                a2_data[i], b2_data[i], c2_data[i],
                color=color, linewidth=linewidth, linestyle=linestyle,
                alpha=alpha, label='Tie Lines' if i == 0 else None, **kwargs
            )
            lines.append(line)
        
        # Add phase points if requested
        if show_points:
            self.scatter_ternary(a1_data, b1_data, c1_data,
                               c=point_colors[0], s=point_sizes[0], 
                               marker=point_markers[0], label=labels[0],
                               alpha=0.8, edgecolors='black', linewidth=1)
            
            self.scatter_ternary(a2_data, b2_data, c2_data,
                               c=point_colors[1], s=point_sizes[1], 
                               marker=point_markers[1], label=labels[1],
                               alpha=0.8, edgecolors='black', linewidth=1)
        
        return lines
    
    def add_plait_point(self, a_plait: float, b_plait: float, c_plait: float,
                       color: str = 'black', size: float = 150, marker: str = '*',
                       label: str = 'Plait Point', **kwargs):
        """
        Add a plait point (critical point) to the diagram.
        
        Parameters:
        -----------
        a_plait, b_plait, c_plait : float
            Component fractions at the plait point
        color : str
            Point color
        size : float
            Point size
        marker : str
            Point marker
        label : str
            Label for legend
        **kwargs
            Additional arguments passed to scatter method
            
        Returns:
        --------
        scatter : matplotlib PathCollection
            The plait point object
        """
        return self.scatter_ternary([a_plait], [b_plait], [c_plait],
                                   c=color, s=size, marker=marker, label=label,
                                   edgecolors='white', linewidth=2, **kwargs)
    
    def add_extraction_region(self, envelope_data: Dict[str, Union[List, np.ndarray]],
                             fill_color: str = 'lightblue', fill_alpha: float = 0.3,
                             boundary_color: str = 'blue', boundary_linewidth: float = 2,
                             label: str = 'Two-Phase Region'):
        """
        Add and highlight the two-phase extraction region.
        
        Parameters:
        -----------
        envelope_data : dict
            Dictionary with keys 'a', 'b', 'c' containing solubility envelope points
        fill_color : str
            Fill color for the region
        fill_alpha : float
            Fill transparency
        boundary_color : str
            Boundary line color
        boundary_linewidth : float
            Boundary line width
        label : str
            Label for the region
        """
        a_env = np.asarray(envelope_data['a'])
        b_env = np.asarray(envelope_data['b'])
        c_env = np.asarray(envelope_data['c'])
        
        # Add the envelope boundary
        self.add_solubility_envelope(a_env, b_env, c_env,
                                   color=boundary_color, linewidth=boundary_linewidth,
                                   fill=True, fill_alpha=fill_alpha, label=label)
        
        return True
