"""
Test suite for the extraction-triangle library.
"""

import unittest
import numpy as np
from extraction_triangle import RightTrianglePlot, RightTriangleCoordinates
from extraction_triangle.utils import validate_data, normalize_data, check_triangle_bounds


class TestRightTriangleCoordinates(unittest.TestCase):
    """Test the coordinate system functionality."""
    
    def setUp(self):
        self.coords = RightTriangleCoordinates("bottom-left")
    
    def test_coordinate_conversion(self):
        """Test conversion between triangle and Cartesian coordinates."""
        u, v = 0.5, 0.3
        x, y = self.coords.to_cartesian(u, v)
        u_back, v_back = self.coords.from_cartesian(x, y)
        
        self.assertAlmostEqual(u, u_back, places=10)
        self.assertAlmostEqual(v, v_back, places=10)
    
    def test_triangle_bounds(self):
        """Test triangle boundary validation."""
        # Valid points
        self.assertTrue(self.coords.is_inside_triangle(0.3, 0.4))
        self.assertTrue(self.coords.is_inside_triangle(0.5, 0.5))
        
        # Invalid points
        self.assertFalse(self.coords.is_inside_triangle(0.7, 0.8))  # u + v > 1
        self.assertFalse(self.coords.is_inside_triangle(-0.1, 0.5))  # u < 0
        self.assertFalse(self.coords.is_inside_triangle(0.5, -0.1))  # v < 0
    
    def test_orientation_validation(self):
        """Test orientation parameter validation."""
        valid_orientations = ["bottom-left", "bottom-right", "top-left", "top-right"]
        
        for orientation in valid_orientations:
            coords = RightTriangleCoordinates(orientation)
            self.assertEqual(coords.orientation, orientation)
        
        with self.assertRaises(ValueError):
            RightTriangleCoordinates("invalid-orientation")
    
    def test_triangle_vertices(self):
        """Test triangle vertex generation."""
        x_verts, y_verts = self.coords.get_triangle_vertices()
        
        # Should have 4 points (closed triangle)
        self.assertEqual(len(x_verts), 4)
        self.assertEqual(len(y_verts), 4)
        
        # First and last points should be the same (closed)
        self.assertEqual(x_verts[0], x_verts[-1])
        self.assertEqual(y_verts[0], y_verts[-1])


class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_validate_data(self):
        """Test data validation function."""
        # Valid data
        valid_data = [1, 2, 3, 4, 5]
        validated = validate_data(valid_data)
        np.testing.assert_array_equal(validated, np.array(valid_data))
        
        # Empty data should raise error
        with self.assertRaises(ValueError):
            validate_data([])
        
        # NaN data should raise error
        with self.assertRaises(ValueError):
            validate_data([1, 2, np.nan, 4])
    
    def test_normalize_data(self):
        """Test data normalization function."""
        data = [1, 2, 3, 4, 5]
        normalized = normalize_data(data, 0, 1)
        
        # Should be between 0 and 1
        self.assertTrue(np.all(normalized >= 0))
        self.assertTrue(np.all(normalized <= 1))
        
        # Min should be 0, max should be 1
        self.assertAlmostEqual(np.min(normalized), 0)
        self.assertAlmostEqual(np.max(normalized), 1)
    
    def test_check_triangle_bounds(self):
        """Test triangle bounds checking and clipping."""
        # Valid points should remain unchanged
        u, v = np.array([0.3, 0.4]), np.array([0.4, 0.2])
        u_clipped, v_clipped = check_triangle_bounds(u, v)
        np.testing.assert_array_almost_equal(u, u_clipped)
        np.testing.assert_array_almost_equal(v, v_clipped)
        
        # Invalid points should be clipped
        u, v = np.array([0.7, -0.1]), np.array([0.8, 0.5])
        u_clipped, v_clipped = check_triangle_bounds(u, v)
        
        # All clipped points should be valid
        self.assertTrue(np.all(u_clipped >= 0))
        self.assertTrue(np.all(v_clipped >= 0))
        self.assertTrue(np.all(u_clipped + v_clipped <= 1.01))  # Small tolerance


class TestRightTrianglePlot(unittest.TestCase):
    """Test the main plotting class."""
    
    def setUp(self):
        self.plot = RightTrianglePlot()
    
    def test_plot_creation(self):
        """Test basic plot creation."""
        self.assertIsNotNone(self.plot.fig)
        self.assertIsNotNone(self.plot.ax)
        self.assertIsNotNone(self.plot.coordinates)
    
    def test_scatter_plot(self):
        """Test scatter plot functionality."""
        u = [0.1, 0.3, 0.5]
        v = [0.2, 0.4, 0.3]
        
        scatter = self.plot.scatter(u, v)
        self.assertIsNotNone(scatter)
    
    def test_line_plot(self):
        """Test line plot functionality."""
        u = np.linspace(0, 0.8, 10)
        v = 0.9 - u
        v = np.clip(v, 0, 1 - u)  # Ensure valid coordinates
        
        line = self.plot.plot(u, v)
        self.assertIsNotNone(line)
    
    def test_grid_addition(self):
        """Test grid addition."""
        # Should not raise any errors
        self.plot.add_grid(n_lines=5)
    
    def test_label_addition(self):
        """Test label addition."""
        # Should not raise any errors
        self.plot.add_labels("Test U", "Test V")


if __name__ == "__main__":
    unittest.main()
