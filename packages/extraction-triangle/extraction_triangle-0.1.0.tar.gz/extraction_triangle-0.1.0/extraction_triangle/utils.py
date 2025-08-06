"""
Utility functions for the extraction triangle library.
"""

import numpy as np
from typing import Union, Tuple, List


def validate_data(data: Union[List, np.ndarray]) -> np.ndarray:
    """
    Validate and convert input data to numpy array.
    
    Parameters:
    -----------
    data : list or array-like
        Input data to validate
        
    Returns:
    --------
    validated_data : np.ndarray
        Validated numpy array
        
    Raises:
    -------
    ValueError
        If data is empty or contains invalid values
    """
    data = np.asarray(data)
    
    if data.size == 0:
        raise ValueError("Data cannot be empty")
    
    if np.any(np.isnan(data)) or np.any(np.isinf(data)):
        raise ValueError("Data cannot contain NaN or infinite values")
    
    return data


def normalize_data(data: Union[List, np.ndarray], 
                  min_val: float = 0.0, 
                  max_val: float = 1.0) -> np.ndarray:
    """
    Normalize data to a specified range.
    
    Parameters:
    -----------
    data : list or array-like
        Input data to normalize
    min_val : float
        Minimum value of output range
    max_val : float
        Maximum value of output range
        
    Returns:
    --------
    normalized_data : np.ndarray
        Normalized data in the specified range
    """
    data = validate_data(data)
    
    data_min = np.min(data)
    data_max = np.max(data)
    
    if data_min == data_max:
        # All values are the same
        return np.full_like(data, (min_val + max_val) / 2)
    
    # Normalize to [0, 1] then scale to [min_val, max_val]
    normalized = (data - data_min) / (data_max - data_min)
    return normalized * (max_val - min_val) + min_val


def check_triangle_bounds(u: Union[float, np.ndarray], 
                         v: Union[float, np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Check and clip coordinates to stay within triangle bounds.
    
    Parameters:
    -----------
    u, v : float or array-like
        Right triangle coordinates
        
    Returns:
    --------
    u_clipped, v_clipped : tuple of arrays
        Coordinates clipped to triangle bounds
    """
    u = np.asarray(u)
    v = np.asarray(v)
    
    # Clip to [0, 1] range
    u = np.clip(u, 0, 1)
    v = np.clip(v, 0, 1)
    
    # Ensure u + v <= 1
    sum_uv = u + v
    over_limit = sum_uv > 1
    
    if np.any(over_limit):
        # Scale down proportionally
        scale_factor = 1.0 / sum_uv
        u = np.where(over_limit, u * scale_factor, u)
        v = np.where(over_limit, v * scale_factor, v)
    
    return u, v


def interpolate_triangle(u: np.ndarray, v: np.ndarray, values: np.ndarray, 
                        u_interp: np.ndarray, v_interp: np.ndarray) -> np.ndarray:
    """
    Interpolate values within the triangle using barycentric coordinates.
    
    Parameters:
    -----------
    u, v : np.ndarray
        Known coordinates
    values : np.ndarray
        Known values at the coordinates
    u_interp, v_interp : np.ndarray
        Coordinates where to interpolate
        
    Returns:
    --------
    interpolated_values : np.ndarray
        Interpolated values
    """
    from scipy.spatial import Delaunay
    from scipy.interpolate import LinearNDInterpolator
    
    # Create points array
    points = np.column_stack([u, v])
    interp_points = np.column_stack([u_interp, v_interp])
    
    # Create interpolator
    interpolator = LinearNDInterpolator(points, values, fill_value=np.nan)
    
    return interpolator(interp_points)


def generate_extraction_curve(x_feed: float, x_extract: float, x_raffinate: float,
                             n_points: int = 100) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate an extraction curve for liquid-liquid extraction.
    
    Parameters:
    -----------
    x_feed : float
        Feed composition
    x_extract : float
        Extract composition
    x_raffinate : float
        Raffinate composition
    n_points : int
        Number of points on the curve
        
    Returns:
    --------
    u_curve, v_curve : tuple of arrays
        Extraction curve coordinates
    """
    # Simple linear extraction curve (can be extended for more complex models)
    t = np.linspace(0, 1, n_points)
    
    # Interpolate between raffinate and extract
    u_curve = x_raffinate + t * (x_extract - x_raffinate)
    v_curve = (1 - x_raffinate) + t * ((1 - x_extract) - (1 - x_raffinate))
    
    # Ensure points stay within triangle
    u_curve, v_curve = check_triangle_bounds(u_curve, v_curve)
    
    return u_curve, v_curve


def calculate_triangle_area(u1: float, v1: float, u2: float, v2: float, 
                          u3: float, v3: float) -> float:
    """
    Calculate the area of a triangle given three points in right triangle coordinates.
    
    Parameters:
    -----------
    u1, v1, u2, v2, u3, v3 : float
        Coordinates of the three triangle vertices
        
    Returns:
    --------
    area : float
        Area of the triangle
    """
    # Use the shoelace formula
    area = 0.5 * abs((u1 * (v2 - v3) + u2 * (v3 - v1) + u3 * (v1 - v2)))
    return area


def calculate_distribution_coefficient(c_extract: Union[float, np.ndarray], 
                                     c_raffinate: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate distribution coefficient K = C_extract / C_raffinate.
    
    Parameters:
    -----------
    c_extract : float or array-like
        Concentration in extract phase
    c_raffinate : float or array-like
        Concentration in raffinate phase
        
    Returns:
    --------
    k : float or array
        Distribution coefficient
    """
    c_extract = np.asarray(c_extract)
    c_raffinate = np.asarray(c_raffinate)
    
    # Avoid division by zero
    c_raffinate = np.where(c_raffinate == 0, 1e-10, c_raffinate)
    
    return c_extract / c_raffinate


def calculate_selectivity(k_solute: Union[float, np.ndarray], 
                         k_diluent: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """
    Calculate selectivity β = K_solute / K_diluent.
    
    Parameters:
    -----------
    k_solute : float or array-like
        Distribution coefficient of solute
    k_diluent : float or array-like
        Distribution coefficient of diluent
        
    Returns:
    --------
    selectivity : float or array
        Selectivity factor
    """
    k_solute = np.asarray(k_solute)
    k_diluent = np.asarray(k_diluent)
    
    # Avoid division by zero
    k_diluent = np.where(k_diluent == 0, 1e-10, k_diluent)
    
    return k_solute / k_diluent


def fit_envelope_polynomial(a_data: np.ndarray, b_data: np.ndarray, 
                           degree: int = 3) -> callable:
    """
    Fit a polynomial to solubility envelope data.
    
    Parameters:
    -----------
    a_data, b_data : np.ndarray
        Component fractions for envelope points
    degree : int
        Degree of polynomial fit
        
    Returns:
    --------
    envelope_func : callable
        Function that returns b given a
    """
    # Sort data by a-component
    sort_idx = np.argsort(a_data)
    a_sorted = a_data[sort_idx]
    b_sorted = b_data[sort_idx]
    
    # Fit polynomial
    coeffs = np.polyfit(a_sorted, b_sorted, degree)
    
    def envelope_func(a):
        return np.polyval(coeffs, a)
    
    return envelope_func


def generate_tie_line_data(a_phase1: np.ndarray, b_phase1: np.ndarray,
                          k_values: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate corresponding phase 2 data from phase 1 data and distribution coefficients.
    
    Parameters:
    -----------
    a_phase1, b_phase1 : np.ndarray
        Component fractions in phase 1
    k_values : np.ndarray
        Distribution coefficients for component A
        
    Returns:
    --------
    a_phase2, b_phase2 : tuple of arrays
        Component fractions in phase 2
    """
    a_phase2 = k_values * a_phase1
    
    # Simple approximation for component B distribution
    # (in reality, this would depend on the specific system)
    k_b = 0.5  # Assumed distribution coefficient for component B
    b_phase2 = k_b * b_phase1
    
    # Ensure valid fractions
    total_phase2 = a_phase2 + b_phase2
    c_phase2 = 1 - total_phase2
    
    # Clip to valid range
    c_phase2 = np.clip(c_phase2, 0, 1)
    
    # Renormalize if needed
    total = a_phase2 + b_phase2 + c_phase2
    a_phase2 /= total
    b_phase2 /= total
    
    return a_phase2, b_phase2


def validate_ternary_data(a: np.ndarray, b: np.ndarray, c: np.ndarray, 
                         tolerance: float = 1e-6) -> bool:
    """
    Validate that ternary data sums to 1.
    
    Parameters:
    -----------
    a, b, c : np.ndarray
        Component fractions
    tolerance : float
        Tolerance for sum check
        
    Returns:
    --------
    valid : bool
        True if data is valid
    """
    totals = a + b + c
    return np.all(np.abs(totals - 1.0) < tolerance)


def interpolate_envelope(a_data: np.ndarray, b_data: np.ndarray, c_data: np.ndarray,
                        n_points: int = 100, method: str = 'cubic') -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Interpolate solubility envelope data to create smooth curves.
    
    Parameters:
    -----------
    a_data, b_data, c_data : np.ndarray
        Original envelope data points
    n_points : int
        Number of interpolated points
    method : str
        Interpolation method ('linear', 'cubic', 'quadratic')
        
    Returns:
    --------
    a_interp, b_interp, c_interp : tuple of arrays
        Interpolated envelope points
    """
    from scipy.interpolate import interp1d
    
    # Create parameter for interpolation
    t = np.linspace(0, 1, len(a_data))
    t_new = np.linspace(0, 1, n_points)
    
    # Interpolate each component
    f_a = interp1d(t, a_data, kind=method, bounds_error=False, fill_value='extrapolate')
    f_b = interp1d(t, b_data, kind=method, bounds_error=False, fill_value='extrapolate')
    f_c = interp1d(t, c_data, kind=method, bounds_error=False, fill_value='extrapolate')
    
    a_interp = f_a(t_new)
    b_interp = f_b(t_new)
    c_interp = f_c(t_new)
    
    # Ensure valid fractions
    a_interp = np.clip(a_interp, 0, 1)
    b_interp = np.clip(b_interp, 0, 1)
    c_interp = np.clip(c_interp, 0, 1)
    
    # Normalize to ensure sum = 1
    total = a_interp + b_interp + c_interp
    a_interp /= total
    b_interp /= total
    c_interp /= total
    
    return a_interp, b_interp, c_interp
